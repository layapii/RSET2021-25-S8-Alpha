from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import tempfile
import shutil
import webbrowser

app = Flask(__name__)
CORS(app)

# Configuration
DUPLICATES_FOLDER_NAME = "Duplicates"

def authenticate_google_drive(access_token):
    """Verify the access token and create Google Drive service"""
    try:
        creds = Credentials(access_token)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return None

@app.route('/save-token', methods=['POST'])
def save_token():
    data = request.json
    access_token = data.get('accessToken')

    if not access_token:
        return jsonify({'error': 'No access token provided'}), 400

    print(f"Received Google Token: {access_token}")  # Log partial token
    return jsonify({'message': 'Token received successfully'})

@app.route('/run-deduplication', methods=['POST'])
def run_deduplication():
    data = request.json
    access_token = data.get('accessToken')
    
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 400
    
    try:
        service = authenticate_google_drive(access_token)
        if not service:
            return jsonify({'error': 'Google authentication failed'}), 500
        
        print("Google Drive authentication successful")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        print(f"Created temp directory: {temp_dir}")
        
        # Run deduplication
        result = subprocess.run(
            [sys.executable, 'deduplication.py', access_token, temp_dir],
            capture_output=True,
            text=True
        )
        
        print("\n=== Process Output ===")
        print(f"Return code: {result.returncode}")
        print(f"stdout:\n{result.stdout}")
        if result.returncode != 0:
            print(f"stderr:\n{result.stderr}")
            raise Exception(result.stderr or "Deduplication failed")
        
        # Parse output for duplicates count
        duplicates_found = 0
        for line in result.stdout.split('\n'):
            if "duplicate pairs" in line.lower():
                duplicates_found = int(line.split()[0])
                break
        
        return jsonify({
            'message': 'Deduplication completed successfully',
            'duplicates_found': duplicates_found
        })
        
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Type: {type(e).__name__}")
        print(f"Details: {str(e)}")
        return jsonify({
            'error': 'Deduplication failed',
            'details': str(e)
        }), 500
    finally:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Cleaned up temp directory: {temp_dir}")
@app.route('/list-folders', methods=['POST'])
def list_folders():
    data = request.json
    access_token = data.get('accessToken')
    folder_name = data.get('folderName')  # Get the folder name from request

    if not access_token:
        return jsonify({'error': 'No access token provided'}), 400

    if not folder_name:
        return jsonify({'error': 'No folder name provided'}), 400

    try:
        service = authenticate_google_drive(access_token)
        
        # Search for the folder by name
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        results = service.files().list(q=query).execute()
        folders = results.get('files', [])

        if not folders:
            return jsonify({'error': 'Folder not found'}), 404

        folder_id = folders[0]['id']  # Get the first matching folder
        return jsonify({'folderId': folder_id})

    except Exception as e:
        print(f"Error fetching folders: {str(e)}")
        return jsonify({'error': 'Failed to retrieve folder', 'details': str(e)}), 500
 
 

@app.route('/categorize', methods=['POST'])
def categorize():
    data = request.json
    access_token = data.get('accessToken')
    folder_name = data.get('folderName')

    if not access_token:
        return jsonify({'error': 'No access token provided'}), 400
    if not folder_name:
        return jsonify({'error': 'No folder name provided'}), 400

    try:
        # Authenticate using the access token
        service = authenticate_google_drive(access_token)
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        results = service.files().list(q=query).execute()
        folders = results.get('files', [])

        if not folders:
            return jsonify({'error': 'Folder not found'}), 404

        folder_id = folders[0]['id']

        # 🧠 Run categorization.py with folder_id and access_token
        subprocess.run(['python3', 'categorization.py', folder_id, access_token], check=True)

    #📂 Open the folder in a browser (or send URL back to frontend)
        folder_url = f'https://drive.google.com/drive/folders/{folder_id}'
        webbrowser.open(folder_url)  # Optional: Only opens server-side

        return jsonify({'success': True, 'folderId': folder_id, 'folderUrl': folder_url})

    except Exception as e:
        print(f"Error during categorization: {str(e)}")
        return jsonify({'error': 'Failed to categorize files', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
