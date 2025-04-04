# translate_subtitles.py
from googletrans import Translator
import json
import time

def translate_srt(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    subtitles = []
    translator = Translator()
    
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit():  # Subtitle number
            sub_num = int(lines[i].strip())
            
            # Get timestamp
            i += 1
            if i < len(lines):
                timestamp = lines[i].strip()
                start, end = timestamp.split(' --> ')
                
                # Convert timestamp to seconds
                def time_to_sec(t):
                    h, m, s = t.replace(',', '.').split(':')
                    return float(h) * 3600 + float(m) * 60 + float(s)
                
                # Get English text
                i += 1
                text_en = ""
                while i < len(lines) and lines[i].strip():
                    text_en += lines[i].strip() + " "
                    i += 1
                
                # Translate to Hindi and Malayalam
                try:
                    text_hi = translator.translate(text_en.strip(), dest='hi').text
                    text_ml = translator.translate(text_en.strip(), dest='ml').text
                    print(f"Translated {sub_num}")
                except Exception as e:
                    print(f"Translation failed for {sub_num}: {e}")
                    text_hi = text_ml = text_en
                
                # Add to subtitles list
                subtitles.append({
                    'id': sub_num,
                    'start': time_to_sec(start),
                    'end': time_to_sec(end),
                    'text_en': text_en.strip(),
                    'text_hi': text_hi,
                    'text_ml': text_ml
                })
                
                time.sleep(0.5)  # Prevent too many requests
        i += 1
    
    # Save as JavaScript file
    with open('subtitles.js', 'w', encoding='utf-8') as f:
        f.write('const subtitles = ')
        json.dump(subtitles, f, ensure_ascii=False, indent=2)
        f.write(';')
    
    print("Translation complete! Created subtitles.js")

if __name__ == "__main__":
    translate_srt("Vid 1.srt")