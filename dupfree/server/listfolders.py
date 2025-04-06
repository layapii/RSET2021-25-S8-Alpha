"""from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def authenticate_google_drive(access_token):
   
    creds = Credentials(token=access_token)
    return build('drive', 'v3', credentials=creds)

def find_folder_id(service, folder_name):
   
    page_token = None
    while True:
        response = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            if file['name'] == folder_name:
                print(f"✅ Found folder: {file['name']} (ID: {file['id']})")
                return file['id']
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return None

def list_files_in_folder(service, folder_id, folder_path=""):
   
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            new_folder_path = f"{folder_path}/{item['name']}"
            list_files_in_folder(service, item['id'], new_folder_path)
        else:
            print(f"📄 File: {folder_path}/{item['name']}")

def main():
    access_token = input("🔐 Enter your Google Drive access token: ").strip()
    folder_name = input("📁 Enter folder name to search: ").strip()

    service = authenticate_google_drive(access_token)
    folder_id = find_folder_id(service, folder_name)

    if folder_id:
        print(f"\n📂 Listing files in '{folder_name}' and its subfolders:\n")
        list_files_in_folder(service, folder_id, folder_path=folder_name)
    else:
        print(f"❌ Folder named '{folder_name}' not found in Drive.")

if __name__ == '__main__':
    main()
?"""




import os
import sys
import webbrowser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Authenticate using access token
def authenticate_google_drive(access_token):
    creds = Credentials(token=access_token)
    return build('drive', 'v3', credentials=creds)

def categorize_files(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])

    if not files:
        print("No files found in folder.")
        return

    for file in files:
        file_id = file['id']
        name = file['name']
        mime_type = file['mimeType']

        # Categorize based on MIME type
        if mime_type.startswith('image/'):
            new_folder = 'Images'
        elif mime_type == 'application/pdf':
            new_folder = 'PDFs'
        elif mime_type.startswith('video/'):
            new_folder = 'Videos'
        else:
            new_folder = 'Others'

        # Check or create subfolder
        folder_query = f"name='{new_folder}' and '{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        folder_search = service.files().list(q=folder_query, fields="files(id)").execute()
        folder_list = folder_search.get('files', [])

        if folder_list:
            target_folder_id = folder_list[0]['id']
        else:
            folder_metadata = {
                'name': new_folder,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [folder_id]
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            target_folder_id = folder.get('id')

        # Move file to the categorized folder
        service.files().update(
            fileId=file_id,
            addParents=target_folder_id,
            removeParents=folder_id,
            fields='id, parents'
        ).execute()

        print(f"Moved {name} to {new_folder}")

    # Open folder in browser
    web_url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"Opening folder in browser: {web_url}")
    webbrowser.open(web_url)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python categorization.py <folder_id> <access_token>")
        sys.exit(1)

    folder_id = sys.argv[1]
    access_token = sys.argv[2]

    service = authenticate_google_drive(access_token)
    categorize_files(service, folder_id)
