import cv2
import threading
import os
import time
import smtplib
import RPi.GPIO as GPIO
from gtts import gTTS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from yolov11 import YOLOv11  # Assuming this is a custom module
import serial
import requests
from geopy.geocoders import Nominatim
import speech_recognition as sr
import pyttsx3

# OpenRouteService API Key
API_KEY = "5b3ce3597851110001cf6248bf743466e00c4aba801900966be2f7fb"

# Serial Configuration
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
time.sleep(2)

# Email & SMS Configuration
SENDER_EMAIL = "amaljosek2812@gmail.com"
RECEIVER_EMAILS = ["amaljosek2812@gmail.com", "tinuevolve@gmail.com", "evolvenithin.kochi@gmail.com"]
EMAIL_PASSWORD = "cisj usty axrf dlla"
PHONE_NUMBERS = ["+916238041785", "+919074080481","+919188030428"]

# GPIO Pins
TRIG, ECHO, BUZZER, BUTTON_PIN, NAV_BUTTON = 23, 24, 25, 17, 27

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(NAV_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Flags
navigation_mode = False
stop_navigation = False
navigation_thread = None

# Initialize pyttsx3 TTS engine globally
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# 📍 Function to fetch current location
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io/json").json()
        lat, lon = map(float, response["loc"].split(","))
        print(f"✅ Current Location: {lat}, {lon}")
        return lat, lon
    except Exception as e:
        print("Failed to get current location:", e)
        return None, None

# 🔍 Function to get coordinates from destination name
def get_coordinates(place_name):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(place_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError("Location not found!")

# 🚦 Function to get directions
def get_directions(start, end):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "coordinates": [[start[1], start[0]], [end[1], end[0]]],  # lon, lat
        "format": "geojson"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        directions = response.json()
        if "features" in directions and len(directions["features"]) > 0:
            return directions["features"][0]["properties"]["segments"][0]["steps"]
        else:
            print("No routes found. Try a different destination.")
            return None
    else:
        print(f"Failed to get directions: {response.status_code} - {response.text}")
        return None

# 🎤 Function to recognize voice input for destination
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak your destination...")
        try:
            audio = recognizer.listen(source, timeout=5)
            destination = recognizer.recognize_google(audio)
            print(f"🗺 Destination: {destination}")
            return destination
        except sr.UnknownValueError:
            print("❌ Could not understand the audio.")
            return None
        except sr.RequestError:
            print("❌ Failed to connect to Google API.")
            return None

# 🔊 TTS Functions
def speak(text):
    global stop_navigation
    if stop_navigation:
        engine.stop()
        return
    t = threading.Thread(target=lambda: engine.say(text) or engine.runAndWait())
    t.start()
    while t.is_alive():
        if stop_navigation:
            engine.stop()
            break
        time.sleep(0.1)

def stop_speaking():
    engine.stop()

# 🚗 Navigation Process
def navigation_process():
    global stop_navigation

    if stop_navigation:
        return

    speak("Navigation mode activated.")

    # Step 1: Get current location
    current_location = get_current_location()
    if not current_location or stop_navigation:
        speak("Failed to get current location.")
        return

    # Step 2: Listen for destination
    speak("Please say the destination.")
    destination = recognize_speech()
    if not destination or stop_navigation:
        speak("No destination detected.")
        return

    # Step 3: Get destination coordinates
    try:
        destination_coords = get_coordinates(destination)
        if stop_navigation:
            return
    except ValueError as e:
        speak(str(e))
        return

    # Step 4: Get directions
    speak("Fetching directions.")
    steps = get_directions(current_location, destination_coords)
    if not steps or stop_navigation:
        speak("Failed to fetch directions.")
        return

    # Step 5: Speak directions
    speak(f"Starting navigation to {destination}.")
    for step in steps:
        if stop_navigation:
            return
        instruction = step["instruction"]
        speak(instruction)

# 🚦 Navigation Control
def navigation():
    global navigation_mode, stop_navigation, navigation_thread

    print("Monitoring navigation button...")
    last_state = GPIO.LOW

    try:
        while True:
            current_state = GPIO.input(NAV_BUTTON)
            if current_state == GPIO.HIGH and last_state == GPIO.LOW:  # Button pressed
                navigation_mode = not navigation_mode
                print(f"Navigation mode toggled to: {navigation_mode}")

                if navigation_mode:
                    print("🟢 Navigation mode ON")
                    stop_navigation = False
                    navigation_thread = threading.Thread(target=navigation_process)
                    navigation_thread.start()
                else:
                    print("🔴 Navigation mode OFF")
                    stop_navigation = True
                    stop_speaking()
                    if navigation_thread and navigation_thread.is_alive():
                        print("Waiting for navigation thread to stop...")
                        navigation_thread.join(timeout=1)
                    speak("Navigation mode deactivated.")
                    print("Deactivation message spoken")

                time.sleep(0.3)  # Debounce delay

            last_state = current_state
            time.sleep(0.1)  # Polling interval

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

# 📩 Send SMS
def send_sms():
    message = "Help needed! This is an urgent alert from the Blind Stick system. Please assist immediately."
    try:
        ser.write(b'AT+CMGF=1\r')
        time.sleep(1)
        for number in PHONE_NUMBERS:
            ser.write(f'AT+CMGS="{number}"\r'.encode())
            time.sleep(1)
            ser.write(message.encode())
            ser.write(b'\x1A')
            time.sleep(2)
            print(f"SMS sent to {number}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

# 📧 Send Email
def send_email():
    subject = "Help Needed"
    body = "This is an urgent alert from the Blind Stick system. Please assist immediately."
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = ", ".join(RECEIVER_EMAILS)
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAILS, message.as_string())
        server.quit()
        print("Email sent successfully to all recipients")
    except Exception as e:
        print(f"Failed to send email: {e}")

# 🚨 Monitor Help Button
def monitor_button():
    last_state = GPIO.LOW
    while True:
        current_state = GPIO.input(BUTTON_PIN)
        if current_state == GPIO.HIGH and last_state == GPIO.LOW:
            print("🚨 Help button pressed! Sending alerts.")
            send_sms()
            send_email()
            time.sleep(1)  # Debounce
        last_state = current_state
        time.sleep(0.1)

# 🔊 Ultrasonic Distance and Buzzer
def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    timeout = start_time + 0.02

    while GPIO.input(ECHO) == 0:
        start_time = time.time()
        if start_time > timeout:
            return None

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        if stop_time > timeout:
            return None

    return ((stop_time - start_time) * 34300) / 2

def ultrasonic_buzzer():
    while True:
        distance = get_distance()
        if distance is None:
            print("Sensor timeout, retrying...")
            continue

        print(f"Distance: {distance:.2f} cm")

        if distance <= 15:
            beep_rate = 10
        elif distance <= 25:
            beep_rate = 5
        elif distance <= 40:
            beep_rate = 2
        else:
            beep_rate = 0

        if beep_rate > 0:
            delay = 1 / (2 * beep_rate)
            GPIO.output(BUZZER, True)
            time.sleep(delay)
            GPIO.output(BUZZER, False)
            time.sleep(delay)
        else:
            GPIO.output(BUZZER, False)

        time.sleep(0.1)

# 🎥 Object Detection
AUDIO_FOLDER = 'audio/'
os.makedirs(AUDIO_FOLDER, exist_ok=True)
detector = YOLOv11()

class VideoStream:
    def _init_(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

def text_to_speech(text):
    audio_file = os.path.join(AUDIO_FOLDER, "output.mp3")
    tts = gTTS(text)
    tts.save(audio_file)
    os.system(f"mpg321 {audio_file} > /dev/null 2>&1")

def start_detection():
    vs = VideoStream(0)
    last_detected = ""
    while True:
        ret, frame = vs.read()
        if not ret:
            print("Failed to capture frame")
            break
        detected_objects = detector.detect_objects(frame)
        if detected_objects:
            detected_names = ', '.join(detected_objects)
            print(f"Detected: {detected_names}")
            if detected_names != last_detected:
                text_to_speech(detected_names)
                last_detected = detected_names
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    vs.stop()


# 🛠 Main Execution
if _name_ == '_main_':
    print("Starting Blind Stick System...")
    threading.Thread(target=start_detection, daemon=True).start()
    threading.Thread(target=monitor_button, daemon=True).start()
    threading.Thread(target=ultrasonic_buzzer, daemon=True).start()
    threading.Thread(target=navigation, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        GPIO.cleanup()
