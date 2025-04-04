import moviepy.editor as mp
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"}) # path to ImageMagick executable
from moviepy.video.VideoClip import TextClip

import time
import os
from dotenv import load_dotenv
from math import ceil
import requests
import random
from gtts import gTTS
from deep_translator import GoogleTranslator
from keybert import KeyBERT
from pydub import AudioSegment
import whisper

kb_model = KeyBERT() # load it on app startup

def generate(summary, category, language):
    start_time = time.time()

# extract a keyphrase using english summary 
    keyphrase = kb_model.extract_keywords(summary, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=1,)[0][0]

# translate summary to target language
    if language != 'en':
        summary = GoogleTranslator(source="auto", target=language).translate(summary)
        print("\nTranslated Summary:", summary)

# gtts and speed up 1.1x to get reel.mp3
    tts = gTTS(summary, lang=language)
    tts.save("outputs/reeel.mp3")
    audio = AudioSegment.from_file("outputs/reeel.mp3")
    faster_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 1.1)}).set_frame_rate(audio.frame_rate)
    faster_audio.export("outputs/reel.mp3", format="mp3")
    os.remove("outputs/reeel.mp3")

# get duration and initialize video
    narration = mp.AudioFileClip("outputs/reel.mp3")
    duration = narration.duration
    print(f'\nDuration = {duration}')
    width, height = 1080, 1920  # aspect ratio 9:16
    video = mp.ColorClip(size=(width, height), color=(0, 0, 0), duration=0)
    
# fetch images using keyphrase
    print(f'\nKeyphrase = {keyphrase}')
    n = ceil(duration/7)
    load_dotenv()
    API_KEY = os.getenv('PEXELS_KEY')
    url = 'https://api.pexels.com/v1/search'
    headers = {'Authorization': API_KEY}
    params = {
        'query': f'{keyphrase}',  # search term
        'per_page': n,  # Number of images 
        'orientation': 'portrait',
    }
    response = requests.get(url, headers=headers, params=params).json()
    for i, photo in enumerate(response['photos'], start=1):
        image_url = photo['src']['original']
        img_data = requests.get(image_url).content
        with open(f'outputs/{i}.jpg', 'wb') as handler:
            handler.write(img_data)
    print(f'\nNo.of images = {n}\n')

# set background images
    backgrounds = []
    for i in range(1, n + 1):
        bg = mp.ImageClip(f'outputs/{i}.jpg').set_duration(7)
        bg = bg.resize(height=height)
        backgrounds.append(bg)
    random.shuffle(backgrounds)
    # fast but no animation
    background = mp.concatenate_videoclips(backgrounds)
    video = mp.CompositeVideoClip([background], size=(width, height))

# find per-second caption chunks
    chunks = {}

    # Transcribe using Whisper if english
    if language == 'en':
        model = whisper.load_model("base")
        transcription = model.transcribe("outputs/reel.mp3", word_timestamps=True)
        # turn it into per-second chunks
        last_word = None
        for segment in transcription["segments"]:
            words = segment.get("words", []) # returns [] if no words data in segment
            for word in words:
                word_start = word["start"]
                word_end = word["end"]
                word_text = word["word"]
                if word_start is None or word_end is None:
                    continue
                # Round timestamps to the nearest second
                start_second = int(word_start)
                end_second = int(word_end)
                # Add word to the correct second
                for second in range(start_second, end_second + 1):
                    if second not in chunks:
                        chunks[second] = [] 
                    if word_text != last_word:  # Avoid repeating words
                        chunks[second].append(word_text)
                        last_word = word_text 

    # Approximate the chunks if not english
    else:
        words = summary.split()
        word_duration = duration / len(words)
        for i, word in enumerate(words):
            second = int(i * word_duration)
            if second not in chunks:
                chunks[second] = []
            chunks[second].append(word)

    # if there is no word for a second
    for second, words in (chunks.items()):
        if words == []: words.append('....')
        print(f"[{second}s]: {' '.join(words)}")

# add captions
    lang_fonts = {"en": "Arial-Bold", "hi": "C:/Windows/Fonts/PRAGATINARROW-BOLD.ttf", "ml": "C:/Windows/Fonts/ANEKMALAYALAM-SEMIBOLD.ttf"}
    # Create a TextClip for each second
    text_clips = []
    for second, words in chunks.items():
        caption_text = ' '.join(words)
        text = TextClip(
            caption_text,
            fontsize=70, 
            color="yellow",
            font=lang_fonts[language],
            stroke_color="black",
            stroke_width=2,
            bg_color="white"
        )
        text = text.set_position(("center", video.h - 400)).set_duration(1).set_start(second)
        text_clips.append(text)
    # Combine the video with the captions
    video = mp.CompositeVideoClip([video, *text_clips])

# write the video file (1fps enough if no animation)
    half_time = time.time()
    video = video.set_audio(narration)
    video.write_videofile("outputs/reel.mp4", fps=1)
    end_time = time.time()
    print(f"Time taken to write reel.mp4 = {end_time - half_time} seconds\n")
    print(f"Total time taken to generate reel = {end_time - start_time} seconds\n")


if __name__ == '__main__':
    summary = "Slovenian handball team makes it to Paris Olympics semifinal Lille, 8 August - Slovenia defeated Norway 33:28 in the Olympic men's handball tournament in Lille late on Wednesday to advance to the semifinal where they will face Denmark on Friday evening. This is the best result the team has so far achieved at the Olympic Games and one of the best performances in the history of Slovenia's team sports squads"
    category = "handball"
    generate(summary, category)