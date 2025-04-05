from googletrans import Translator
from gtts import gTTS
import json
import time
import os
import base64
import sqlite3
from pathlib import Path

class WordTranslationService:
    def __init__(self, db_path='word_translations.db'):
        self.translator = Translator()
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for caching translations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                word TEXT,
                source_lang TEXT,
                meaning TEXT,
                pronunciation TEXT,
                audio_path TEXT,
                PRIMARY KEY (word, source_lang)
            )
        ''')
        conn.commit()
        conn.close()

    def get_cached_translation(self, word, source_lang):
        """Get translation from cache if it exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT meaning, pronunciation, audio_path FROM translations WHERE word=? AND source_lang=?', 
            (word, source_lang)
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                'meaning': result[0],
                'pronunciation': result[1],
                'audioUrl': result[2]
            }
        return None

    def cache_translation(self, word, source_lang, meaning, pronunciation, audio_path):
        """Cache translation in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO translations VALUES (?, ?, ?, ?, ?)',
            (word, source_lang, meaning, pronunciation, audio_path)
        )
        conn.commit()
        conn.close()

    def translate_word(self, word, source_lang):
        """Translate a single word and generate pronunciation"""
        try:
            # Check cache first
            cached = self.get_cached_translation(word, source_lang)
            if cached:
                return cached

            # Translate word
            translation = self.translator.translate(word, src=source_lang, dest='en')
            meaning = translation.text
            pronunciation = translation.pronunciation if translation.pronunciation else word

            # Generate audio file
            audio_dir = Path('audio_cache')
            audio_dir.mkdir(exist_ok=True)
            
            audio_filename = f"{source_lang}_{base64.urlsafe_b64encode(word.encode()).decode()}.mp3"
            audio_path = audio_dir / audio_filename

            if not audio_path.exists():
                tts = gTTS(text=word, lang=source_lang)
                tts.save(str(audio_path))

            # Cache the result
            self.cache_translation(word, source_lang, meaning, pronunciation, str(audio_path))

            return {
                'meaning': meaning,
                'pronunciation': pronunciation,
                'audioUrl': str(audio_path)
            }

        except Exception as e:
            print(f"Translation failed for word '{word}': {e}")
            return None

def process_subtitle_files(subtitle_files):
    """Process all words in multiple subtitle files and create word dictionary"""
    service = WordTranslationService()
    word_dictionary = {'hi': {}, 'ml': {}}

    for subtitle_file in subtitle_files:
        print(f"Processing {subtitle_file}...")
        
        # Read subtitle file with robust parsing for JS module
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract the JSON array part between const declaration and export
            start = content.find('[')
            end = content.rfind(']') + 1
            json_content = content[start:end]
            
            try:
                subtitles = json.loads(json_content)
            except json.JSONDecodeError as e:
                print(f"Error parsing {subtitle_file}: {e}")
                print(f"Problematic content: {json_content[max(0, e.pos-30):e.pos+30]}")
                continue

        # Process each subtitle
        for subtitle in subtitles:
            # Process Hindi words - remove punctuation and split
            hindi_words = [word.strip('।,.!?') for word in subtitle['text_hi'].split()]
            for word in hindi_words:
                if word and word not in word_dictionary['hi']:
                    translation = service.translate_word(word, 'hi')
                    if translation:
                        word_dictionary['hi'][word] = translation
                    time.sleep(0.5)  # Prevent too many requests

            # Process Malayalam words - remove punctuation and split
            malayalam_words = [word.strip('.,!?') for word in subtitle['text_ml'].split()]
            for word in malayalam_words:
                if word and word not in word_dictionary['ml']:
                    translation = service.translate_word(word, 'ml')
                    if translation:
                        word_dictionary['ml'][word] = translation
                    time.sleep(0.5)  # Prevent too many requests

    # Save word dictionary as JavaScript file
    with open('word_dictionary.js', 'w', encoding='utf-8') as f:
        f.write('const wordDictionary = ')
        json.dump(word_dictionary, f, ensure_ascii=False, indent=2)
        f.write(';\n\nexport default wordDictionary;')

if __name__ == "__main__":
    subtitle_files = [
        "src/data/subtitles1.js",
        "src/data/subtitles2.js",
        "src/data/subtitles3.js",
        "src/data/subtitles4.js",
        "src/data/subtitles5.js",
        "src/data/subtitles6.js",
        "src/data/subtitles7.js",
        "src/data/subtitles8.js",
        "src/data/subtitles9.js",
        "src/data/subtitles10.js"
    ]
    process_subtitle_files(subtitle_files)