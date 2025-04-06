import os
import io
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("AIzaSyCdbYqcHJVXtBqMvGLlPvKq2aFq_HzLx6s")

genai.configure(api_key=api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp", generation_config=generation_config)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/extract_text', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)  # Save file to disk
        
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
            image_bytes = io.BytesIO(image_data)
            
            uploaded_file = genai.upload_file(image_bytes, mime_type="image/jpeg")
            
            chat_session = model.start_chat(
                history=[
                    {"role": "user", "parts": [uploaded_file, "Return the text in the image."]}
                ]
            )
            
            response = chat_session.send_message("Please process the image.")
            extracted_text = response.text
        
        return jsonify({'extracted_text': extracted_text, 'file_path': file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)