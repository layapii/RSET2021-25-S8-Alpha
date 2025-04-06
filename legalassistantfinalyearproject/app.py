import io
import json
import os
import threading
import cv2
import fitz
from deep_translator import GoogleTranslator
import PyPDF2
import firebase_admin
import numpy as np
import requests
import base64
from fpdf import FPDF
from flask import Flask, logging, render_template, request, send_file, session, redirect, url_for, jsonify
from firebase_admin import auth, initialize_app, credentials, firestore
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from concurrent.futures import ThreadPoolExecutor
import spacy
import mysql.connector
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
app = Flask(__name__)

CORS(app, supports_credentials=True)  # Fixes CORS
from flask import Flask, render_template, request, redirect, session, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from pdf2image import convert_from_bytes, convert_from_path
import io
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

if 'first_app' not in firebase_admin._apps:
    cred1 = credentials.Certificate('templates/fire.json')
    default_app1 = firebase_admin.initialize_app(cred1, name='first_app')
    db1 = firestore.client(app=default_app1)

# Initialize the second Firebase app
if 'second_app' not in firebase_admin._apps:
    cred2 = credentials.Certificate('templates/firebaseconfig.json')
    default_app2 = firebase_admin.initialize_app(cred2, name='second_app')
    db2 = firestore.client(app=default_app2)

nlp = spacy.load("en_core_web_sm")
# Establish a connection
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Basileldo',
        database='advocate_db'
    )
    if conn.is_connected():
        print("Connection to MySQL database established successfully!")
        
    cursor = conn.cursor(dictionary=True)
    print("Cursor created:", cursor)
    
except mysql.connector.Error as err:
    print(f"Error: {err}")
# Initialize Firebase Admin SDK
try:
    # Initialize Firebase Admin SDK with service account credentials
    cred = credentials.Certificate(r'templates/firebaseconfig.json')  # Path to your service account key file
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully!")
except Exception as e:
    logging.error("Failed to initialize Firebase Admin SDK")
    logging.error(f"Error details: {str(e)}")
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize model and prompt
template = """
You are an AI Legal Assistant specializing in Indian law. Use clear, concise, and structured language to provide accurate legal advice tailored to the scenario. 

Here is the conversation history: {context}

Question: {question}

Provide a step-by-step response, including:
1. A brief overview of the legal context or relevant laws applicable in India.
2. Key legal steps or actions the user should take, with examples or explanations as needed.
3. Any relevant legal documents, authorities, or organizations involved.
4. Common pitfalls, rights, or protections that may apply.
5. A summary of next steps, including any potential outcomes or additional advice if required.
"""


# Greeting responses
greeting_responses = {
    "hi": "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hello": "Hi there! I provide legal assistance specific to India. What do you need help with?",
    "how are you": "I'm here to assist you with legal information in India!",
    "hey": "Hey! What legal information do you need regarding Indian laws?",
    "can you help": "Absolutely! Please describe your legal issue, and I'll provide the best advice based on Indian law.",
    "hii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hiiii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "how are you" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hiiiiii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hai" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "haii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hiii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?"
}

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        print(email)
        try:
            user = auth.get_user_by_email(email)
            print(user.uid)
            session['user_id']=user.uid
            print(user)
            session['username'] = email
            print("jfbndf")
            return jsonify({'message': 'Login successful'})
        except Exception as e:
            print("Error logging in:", e)
            return jsonify({'message': 'Login failed'}), 401

@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    user_id = session.get('user_id')
    username = session.get('username') 
    print(username) # Get the user_id from the session
    if user_id:
        return jsonify({'user_id': user_id,'username':username})

    else:
        return jsonify({'message': 'User not logged in'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return render_template('authenti.html')


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    address = data.get('address')
    pincode = data.get('pincode')
    
    try:
        user = auth.create_user(email=email, password=password, display_name=username)
        return jsonify({'message': 'User created successfully'}), 200
    except Exception as e:
        print("Error creating user:", e)
        return jsonify({'message': 'Failed to create user'}), 400


from groq import Groq
os.environ["GROQ_API_KEY"] = "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"
# Return transliterated JSON response
client = Groq()
@app.route('/generate_pdf', methods=['POST'])

def generate_pdf():
    # Step 1: Receive lease details from the request
    
    lease_details = request.form.get('lease_details')
    language=request.form.get('language')
    print(language)
    print(lease_details)
    import requests
    import re

    import requests
    import re

    def google_transliterate(text, lang="ml"):
        """Transliterates English text to Malayalam using Google's API, safely handling API response errors."""
        
        if not isinstance(text, str) or not text.strip() or re.match(r"^\d{1,4}[/.-]\d{1,2}[/.-]\d{1,4}$", text):
            return text  # Return unchanged if it's not a valid string or a date

        url = f"https://www.google.com/inputtools/request?text={text}&itc={lang}-t-i0-und&num=1"

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure before accessing indices
                if isinstance(data, list) and len(data) > 1:
                    transliteration_data = data[1]
                    if isinstance(transliteration_data, list) and len(transliteration_data) > 0:
                        first_suggestion = transliteration_data[0]
                        if isinstance(first_suggestion, list) and len(first_suggestion) > 1:
                            transliterations = first_suggestion[1]
                            if isinstance(transliterations, list) and len(transliterations) > 0:
                                return transliterations[0]  # Return the first transliteration suggestion
            
        except requests.RequestException as e:
            print(f"API Request Failed: {e}")  # Log request failure for debugging

        return text  # Return original text if an error occurs


    def transliterate_json(data, lang):
        """Recursively transliterates only the provided values in a JSON object, skipping 'not provided' values."""
        
        def should_skip(value):
            """Checks if the value should be skipped from transliteration."""
            return value in [None, "", "not provided", "Not provided", "NOT PROVIDED"]
        
        if isinstance(data, dict):
            return {key: transliterate_json(value, lang) if not should_skip(value) else value for key, value in data.items()}  
            # Keeps None, empty strings, and "not provided" unchanged
        
        elif isinstance(data, list):
            return [transliterate_json(item, lang) for item in data]  # Process lists recursively
        
        elif isinstance(data, str) and not should_skip(data):  # Only process non-empty, non-skipped strings
            return google_transliterate(data, lang)
        
        return data  # Return unchanged for skipped values (None, empty, "not provided", numbers, etc.)


    if not lease_details:
        return jsonify({'error': 'Lease details are required!'}), 400
    
    # Step 2: Prepare the document type based on the input
    document_type = "lease"  # Default type, can adjust based on input
    if "copyright" in lease_details.lower():
        document_type = "copyright"
    elif "contract" in lease_details.lower():
        document_type = "contract"
    elif "copyright" in lease_details.lower():
        document_type = "copyright"

    # Step 3: Prepare the prompt for the Llama model based on the document type
    if document_type == "lease":
        prompt = f"""
        Given the following lease details paragraph:

        {lease_details}

        Extract the information and structure it into a JSON object with these attributes:
        - Effective Date (DD/MM/YYYY format)
        - Lessor Information (Name, Parent's Name, Age, Address)
        - Lessee Information (Name, Parent's Name, Age, Address)
        - Property Details (Property Number, Total Area, Property Location,Pin Code,Country)
        - Lease Terms (Term Duration, Monthly Lease Amount, Security Deposit,Security Deposit(in words), Payment Due Date)
        - Other Clauses (Late Charges, Conditions for Security Deposit, Termination Notice Period)
        ***there should not be any spaces in keys not replace it with '_' in the output json
        Each attribute should be filled with the corresponding value from the paragraph, or left blank if not found.
        The output should be a well-structured JSON object based on these attributes.
        **Rules for Extraction:**  
1. Extract the exact values from the provided text without inference or guessing.  
2. If any detail is missing in the text, return `"Not provided"`.  
        """
    
    elif document_type == "copyright":
        prompt = f"""
        Given the following copyright agreement details paragraph:

        {lease_details}

        Extract the relevant information and structure it into a JSON object with the following attributes:
        - Effective Date (DD/MM/YYYY format)
        - Author Information (Name, Parent's Name, Age, Address)
        - Publisher Information (Name, Parent's Name, Age, Address)
        - Copyright Details (Work Title, Work Type, Copyright Registration Number, Copyright Duration)
        - License Terms (Licensing Scope, Royalty Percentage, Payment Schedule)
        - Other Clauses (Exclusivity, Termination Conditions, Territory)

        Each attribute should be filled with the corresponding value from the paragraph.
        If any attribute is missing, leave it blank. The output should be a well-structured JSON object based on these attributes.
        Language Output: Output the extracted information in the language provided by the user.the language is{language}
        """
    elif document_type=="contract":
        prompt = f"""
Given the following contract agreement details paragraph:
{lease_details}Extract relevant information from the given contract details and structure it into a JSON object with the following attributes:

Effective Date (DD/MM/YYYY format)

Parties Involved

First Party (Name, Parent's Name, Age, Address)

Second Party (Name, Parent's Name, Age, Address)

Contract Details

Contract Title

Contract Type (e.g., Employment, Service, Partnership)

Contract Duration (Start Date, End Date)

Financial Terms

Payment Amount

Payment Frequency (Monthly, Yearly, One-time)

Late Payment Penalties

Obligations & Responsibilities

First Party Obligations

Second Party Obligations

Termination & Legal Clauses

Termination Conditions

Dispute Resolution Mechanism

Confidentiality Clause

Governing Law (Jurisdiction)

If any attribute is missing, mark it as 'Not provided'.
        """
    
    else:
        return jsonify({'error': 'Unknown document type'}), 400

    # Step 4: Send the request to the Llama model for analysis
    print("Step 2: Sending request to Llama model for analysis.")
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[ 
            {"role": "system", "content": """
            You are a highly accurate legal content extractor. Your task is to extract detailed information from the provided legal agreements. Follow these instructions:
            1. *Data Extraction*: Extract the following fields based on the document type:
                - For Lease Agreement: Effective Date, Lessor Information (Name, Parent's Name, Age, Address), Lessee Information (Name, Parent's Name, Age, Address), Property Details (Property Number, Total Area, Property Location), Lease Terms (Term Duration, Monthly Lease Amount, Security Deposit, Payment Due Date), Other Clauses (Late Charges, Conditions for Security Deposit, Termination Notice Period)
                - For Copyright Agreement: Effective Date, Author Information (Name, Parent's Name, Age, Address), Publisher Information (Name, Parent's Name, Age, Address), Copyright Details (Work Title, Work Type, Copyright Registration Number, Copyright Duration), License Terms (Licensing Scope, Royalty Percentage, Payment Schedule), Other Clauses (Exclusivity, Termination Conditions, Territory)

            2. *Handling Missing Information*: If any information is missing, mark it as 'Not provided'.
            3. *Ensure Exact Matches*: Match the data exactly as it is presented in the input. Do not infer or guess information.
            4. *Formatting*: Output the extracted information in the following **exact JSON format**:
            {
                "Effective_Date": "DD/MM/YYYY",
                "Author_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
                "Publisher_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
                "Copyright_Details": {"Work_Title": "Title", "Work_Type": "Type", "Copyright_Registration_Number": "Registration Number", "Copyright_Duration": "Duration"},
                "License_Terms": {"Licensing_Scope": "Scope", "Royalty_Percentage": "Percentage", "Payment_Schedule": "Schedule"},
                "Other_Clauses": {"Exclusivity": "Exclusivity", "Termination_Conditions": "Conditions", "Territory": "Territory"}
            }

            5. *Quality Assurance*: Ensure that all fields are filled accurately and completely. If a piece of information is not found in the text, return 'Not provided'.

            """},
            {"role": "user", "content": prompt}
        ],
        temperature=0.001,
        max_tokens=1024,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"}
    )

    # Step 5: Collect the response from the model
    bot_reply = completion.choices[0].message.content
    extracted_data = ""
    try:
        extracted_data = json.loads(bot_reply)  # Attempt to parse JSON response
        print("JSON generated successfully.")
    except json.JSONDecodeError as e:
        return jsonify({'error': 'Failed to parse JSON response', 'details': str(e)}), 500
    print(extracted_data)
    

    # If there are missing fields, return an alert script
    print(document_type)
    translated_json = transliterate_json(extracted_data, language)
    print(translated_json)
    print("sknnsfv")
    # Firestore document structure
    lease_doc = {
        "extracted_data": translated_json,  # Extracted JSON data
        "document_type": document_type,    # Lease, copyright, or contract
        "user_id": session.get('user_id'),  # Replace with actual user_id
        "language":language
    }
    print(lease_doc)
    doc_ref = db2.collection(document_type).add(lease_doc)
    print(doc_ref)
    if document_type == "lease" and language =="en":
        return render_template('ss.html', data=translated_json)
    elif document_type == "lease" and language =="ml":
        return render_template('ss mal.html', data=translated_json)
    elif document_type == "lease" and language =="ta":
        return render_template('ss tamil.html', data=translated_json)
    elif document_type == "lease" and language =="hi":
        return render_template('ss hindi.html', data=translated_json)
    elif document_type == "copyright":
        return render_template('ss1.html', data=extracted_data)
    elif document_type == "contract" and language =="en":
        return render_template('ss2.html', data=translated_json)
    elif document_type == "contract" and language =="ta":
        return render_template('ss2 tamil.html', data=translated_json)
    elif document_type == "contract" and language =="ml":
        return render_template('ss2 mal.html', data=translated_json)
    elif document_type == "contract" and language =="hi":
        return render_template('ss2 hindi.html', data=translated_json)
from dotenv import load_dotenv

import google.generativeai as genai
os.makedirs('uploads', exist_ok=True)
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")




genai.configure(api_key=api_key)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp", generation_config=generation_config)
import tempfile
@app.route('/extract_text', methods=['POST'])
def extract_text():
    try:
        print("Step 1: Checking if the user uploaded a file...")  # Progress print
        # Check if the user has uploaded a file
        if 'file' not in request.files:
            print("No file uploaded.")
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            print("No file selected.")
            return jsonify({'error': 'No selected file'}), 400
        
        print(f"Step 2: File '{file.filename}' uploaded successfully.")  # Debugging print
        
        # Read the file content directly into memory (raw bytes)
        image_data = file.read()
        print("Step 3: File content read into memory.")  # Debugging print
        
        # Save the image data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name
            print(f"Step 4: Temporary file saved at {temp_file_path}.")  # Debugging print

        # Upload the temporary file to Gemini
        print(f"Step 5: Uploading file '{temp_file_path}' to Gemini...")  # Debugging print
        uploaded_file = genai.upload_file(temp_file_path, mime_type="application/pdf")  # Adjust mime type if needed
        
        print("Step 6: Sending request to extract text from the image...")  # Debugging print
        # Start a chat session with the Gemini model
        chat_session = model.start_chat(
            history=[{
                "role": "user",
                "parts": [
                    uploaded_file,
                    "Return the text in the image. Don't insert line breaks in the output."
                ]
            }]
        )

        # Get the response from the model after processing the image
        response = chat_session.send_message("Please process the image.")
        article = response.text
        print(article)
        print("Step 7: Text extracted successfully.")  # Debugging print
        # Return the extracted text in the response
        return jsonify({'extracted_text': article})

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Print the error if an exception is raised
        return jsonify({'error': str(e)}), 500
    
import sqlite3
import pandas as pd
DATABASE = "advocates.db"
def get_advocates_by_location(location=None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if location:
        cursor.execute("SELECT Name, `Place of Practice`, `Mobile Number` FROM advocates WHERE `Place of Practice` LIKE ?", ('%' + location + '%',))
    else:
        cursor.execute("SELECT Name, `Place of Practice`, `Mobile Number` FROM advocates")  # Fetch all if no location
    
    advocates = cursor.fetchall()
    conn.close()
    return advocates

# ✅ New route for fetching advocates
@app.route("/showadv", methods=["GET"])
def show_advocate():
    location = request.args.get("location", "").strip()
    advocates = get_advocates_by_location(location)
    return render_template("index.html", advocates=advocates, location=location)




@app.route("/advocates", methods=["GET"])
def show_advocates():
    return render_template("index.html")
    
@app.route('/delete_document/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    try:
        db2.collection("lease").document(doc_id).delete()  # Modify collection as needed
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/case', methods=['POST', 'GET'])
def case_input():
    if request.method == 'POST':
        case_scenario = request.form.get('case_scenario')
        # Add your case processing logic here
        return render_template('docgeneration.html', scenario=case_scenario)
    return render_template('docgeneration.html')

# Main routes
@app.route('/')
def index():
    return render_template('authenti.html')

@app.route('/main')
def main():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('main.html')


def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()

UPLOAD_FOLDER = "uploaded_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['pdf']
    print(file)
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save file locally
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(filepath)
    print(extracted_text)

    summary_prompt = f"""
    Given the following extracted copyright agreement details:

    {extracted_text}

    Generate a concise summary highlighting the key points such as:
    - Effective Date
    - Author & Publisher Information
    - Copyright Details
    - Licensing Terms
    - Other Important Clauses

    Ensure the summary is clear, informative, and structured in 3-5 sentences.
    """

    summary_completion = client.chat.completions.create(
        model="llama3-8b-8192",  # Replace with your summarization model if needed
        messages=[
            {"role": "system", "content": "You are an expert legal summarizer. Your task is to create a concise and well-structured summary of legal agreements."},
            {"role": "user", "content": summary_prompt}
        ],
        temperature=0.5,
        max_tokens=512,
        top_p=1,
        stream=False
    )

# Step 7: Collect the summary response
    summary_text = summary_completion.choices[0].message.content
    print("Generated Summary:")
    print(summary_text)
    # Save file path to Firestore
    doc_ref = db2.collection("pdf_files").add({
        "filename": file.filename,
        "filepath": filepath,
        "summary": summary_text  # Store first 500 characters as summary
    })

    return jsonify({'message': 'File uploaded successfully', 'summary': summary_text})

@app.route('/advocates')
def advo():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('advocate.html')

@app.route('/bot')
def bot():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('chatadvice.html')

# Error handlers
@app.route('/view_document/<doc_id>', methods=['GET'])
def view_document(doc_id):
    try:
        collections = ['lease', 'contract', 'copyright']
        
        for collection in collections:
            doc_ref = db2.collection(collection).document(doc_id)
            document = doc_ref.get()

            if document.exists:
                data = document.to_dict()
                document_type = data.get("document_type", collection)
                language = data.get("language", "en")  # Get language from Firestore
                translated_json = data.get("extracted_data", {})

                # Routing based on document_type and language
                if document_type == "lease":
                    if language == "en":
                        return render_template('ss.html', data=translated_json)
                    elif language == "ml":
                        return render_template('ss mal.html', data=translated_json)
                    elif language == "ta":
                        return render_template('ss tamil.html', data=translated_json)
                    elif language == "hi":
                        return render_template('ss hindi.html', data=translated_json)

                elif document_type == "contract":
                    if language == "en":
                        return render_template('ss2.html', data=translated_json)
                    elif language == "ml":
                        return render_template('ss2 mal.html', data=translated_json)
                    elif language == "ta":
                        return render_template('ss2 tamil.html', data=translated_json)
                    elif language == "hi":
                        return render_template('ss2 hindi.html', data=translated_json)

                elif document_type == "copyright":
                    return render_template('ss1.html', data=translated_json)

                return "Unsupported document type or language.", 400

        return "Document not found in any collection.", 404

    except Exception as e:
        print(f"Error fetching document: {e}")
        return "An error occurred while retrieving the document.", 500

@app.route('/fetch_documents', methods=['GET'])
def fetch_documents():
    print("Fetching documents for user...")

    user_id = session.get('user_id') 
    print(user_id) # Retrieve user ID from session
    print("sdkjvnsnvs")
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401  # Return error if user is not logged in

    try:
        # Query Firestore for documents related to the user
        print("Querying Firestore for user_id:", user_id) 
        print("Fetching lease and copyright documents...") 

        documents = []

        # Fetch from 'lease' collection
        lease_docs = db2.collection('lease').where('user_id', '==', user_id).stream()
        for doc in lease_docs:
            data = doc.to_dict()
            documents.append({
                'name': data.get('document_type', 'Lease Document'),
                'id': doc.id,
                'type': 'lease'
            })
        contract_docs = db2.collection('contract').where('user_id', '==', user_id).stream()
        for doc in contract_docs:
            data = doc.to_dict()
            documents.append({
                'name': data.get('document_type', 'Contract Document'),
                'id': doc.id,
                'type': 'contract'
    })
        # Fetch from 'copyright' collection
        copyright_docs = db2.collection('copyright').where('user_id', '==', user_id).stream()
        for doc in copyright_docs:
            data = doc.to_dict()
            documents.append({
                'name': data.get('document_type', 'Copyright Document'),
                'id': doc.id,
                'type': 'copyright'
            })

        print(f"Documents fetched: {documents}")
        return jsonify({'documents': documents}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch documents', 'details': str(e)}), 500
# Process chat route (if needed for non-WebSocket fallback)
@app.route('/process_chat', methods=['POST'])
def process_chat():
    data = request.get_json()
    user_message = data.get("userMessage")
    beh1 = data.get("beh")

    print(f"Persona: {beh1}, User Message: {user_message}")
    
    user_id = session.get('user_id')
    print(f"User ID: {user_id}")

    if user_message:
        prompt = f"""
Act as an advanced AI legal assistant specializing in Indian law. The user needs guidance on:

**"{user_message}"**

Your response should be **concise, structured, and easy to read**. Use **bold text, minimal spacing, and a compact format**. Stick to this structure:

---

<strong>📌 Understanding the Issue:</strong>  
• Summarize the user’s legal query in simple terms.  
• Identify key legal aspects involved.  

<strong>⚖️ Legal Context & Laws:</strong>  
• Explain relevant **Indian laws, acts, and legal principles**.  
• Cite case laws if applicable.  

<strong>🛠️ Step-by-Step Guidance:</strong>  
• Outline **clear steps** the user should take.  

<strong>🔍 Possible Outcomes & Risks:</strong>  
• Highlight potential legal implications.  

<strong>📢 Special Cases & Exceptions:</strong>  
• Mention **exceptions, alternative interpretations, or key edge cases**.  

<strong>🔹 Practical Tips:</strong>  
• Share **best practices and common mistakes to avoid**.  
• Suggest **when to consult a lawyer** for deeper guidance.  

⚠️ **Disclaimer:** This is **informational guidance only**. Consult a lawyer for specific legal advice.

---
Ensure the response is **engaging, professional, and free of unnecessary jargon**.
"""

        persona_styles = {
            "professional": "You are a professional legal consultant. Be direct, structured, and factual.",
            "friendly": "You are a warm and approachable AI. Explain things in a conversational tone.",
            "motivational": "You are a positive and encouraging legal guide. Keep the tone uplifting.",
            "humorous": "You are a witty AI assistant. Make explanations fun but still informative."
        }

        # Set Personality Prompt
        personality_prompt = persona_styles.get(beh1, "You are a knowledgeable legal assistant.")

        # Generate AI response
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[ 
                {"role": "system", "content": personality_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1024,
            top_p=1,
            stream=True
        )

        bot_reply = ""
        for chunk in completion:
            bot_reply += chunk.choices[0].delta.content or ""

        print(bot_reply)

        # Format response with white text and compact spacing
        formatted_reply = f"""
        <div style="font-family: Arial, sans-serif; color: #FFFFFF; line-height: 1.4;">
            <strong style="color: #FFD700;">📜 Legal Advice:</strong><br>
            {bot_reply.replace('\n<strong>', '<br><strong>')
                      .replace('\n- ', '<br>• ')
                      .replace('\n', '<br>')}
            <br><br>
            <strong style="color: #FF4500;">⚖️ Disclaimer:</strong> This is **informational guidance only**. Consult a legal professional for specific advice.
        </div>
        """

        return jsonify({"reply": formatted_reply, "user_id": user_id})

            
        return jsonify({"reply": "Sorry, I couldn't understand your message."})
@app.template_filter('is_dict')
def is_dict(value):
    return isinstance(value, dict)

@app.route('/select_advocate', methods=['GET', 'POST'])
def select_advocate():
    if request.method == 'POST':
        category = request.form.get('category')
        location = request.form.get('location').strip()
        min_experience = request.form.get('min_experience', 0)
        min_rating = request.form.get('min_rating', 0)
        
        # Debug prints
        print(f"Category: {category}")
        print(f"Location: {location}")
        print(f"Min Experience: {min_experience}")
        print(f"Min Rating: {min_rating}")

        # Convert inputs to proper types
        try:
            min_experience = int(min_experience)
            min_rating = float(min_rating)
        except ValueError:
            return "Invalid input for experience or rating", 400

        # Debug: print the formatted query parameters
        print(f"Formatted Params: category={category}, location={location}, experience={min_experience}, rating={min_rating}")
        
        # Query to filter advocates by category, location, experience, and rating
        query = """
        SELECT * FROM advocates
        WHERE category = %s
        AND location LIKE %s
        AND experience >= %s
        AND rating >= %s
        ORDER BY rating DESC
        """
        params = (category, f"%{location}%", min_experience, min_rating)
        
        # Debug: print the SQL query
        print(f"SQL Query: {query}")
        print(f"Params: {params}")
        
        # Execute query
        cursor.execute(query, params)
        result = cursor.fetchall()
        
        # Debug: Check the result
        print(f"Query Result: {result}")
        
        if result:
            return render_template('advocate_results.html', advocates=result)
        else:
            message = "No advocates found with the given criteria."
            return render_template('advocate.html', message=message)

    return render_template('advocate_filter_form.html')

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/v1/chat/completions"
@app.route("/get_ai_suggestions", methods=["POST"])
def get_ai_suggestions():
    data = request.json
    lease_text = data.get("lease_text", "").strip()
     
    if not lease_text:
        return jsonify({"error": "Lease text cannot be empty"}), 400

    aicompletion = client.chat.completions.create(
        model="llama3-8b-8192",  # Check if this model name is correct
        messages=[
            {"role": "system", "content": """Correct the grammar and syntax of the given text while ensuring clarity and professionalism. Maintain the original intent and structure but refine 
             it for a formal agreement. Output only the corrected text without any explanations."""},
            {"role": "user", "content": lease_text}
        ],
        temperature=0.5,
        max_tokens=512,
        top_p=1,
        stream=False
    )

    # Extracting the AI's response correctly
    corrected_text = aicompletion.choices[0].message.content.strip()
    corrected_text = corrected_text.removeprefix("Here is the corrected text:").strip()  # Remove unwanted text


    return jsonify({"corrected_text": corrected_text})


app.jinja_env.filters['is_dict'] = is_dict
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)