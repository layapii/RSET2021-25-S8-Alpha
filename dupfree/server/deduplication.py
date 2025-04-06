import os
import sys
import time
import cv2
import numpy as np
import imagehash
from PIL import Image
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Configuration
THRESHOLD = 0.55
SIFT_THRESHOLD = 0.3
HASH_SIZE = 32
BANDS = 75
DUPLICATES_FOLDER_NAME = "duplicates"
MAX_DUPLICATES_TO_UPLOAD = 50

def find_duplicates(image_paths):
    """Find duplicate images using pHash and SIFT"""
    print("\n[STATUS] Finding duplicate images...")
    
    # Load and resize images
    images = []
    valid_paths = []
    for path in image_paths:
        try:
            with Image.open(path) as img:
                img = img.convert('RGB')
                img = img.resize((256, 256))
                images.append(np.array(img))
                valid_paths.append(path)
        except Exception as e:
            print(f"[WARNING] Error loading {os.path.basename(path)}: {str(e)}")
            continue
    
    if len(images) < 2:
        print("[STATUS] Not enough valid images to compare")
        return []

    processed_pairs = set()
    duplicates = []
    
    # pHash comparison
    print("[STATUS] Running pHash comparison...")
    signatures = {}
    for idx, img in enumerate(images):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            resized = cv2.resize(gray, (HASH_SIZE, HASH_SIZE))
            phash = imagehash.phash(Image.fromarray(resized), hash_size=HASH_SIZE)
            signatures[idx] = phash
        except Exception as e:
            print(f"[WARNING] Error processing image {idx}: {str(e)}")
            continue
    
    # Compare signatures
    for i in range(len(images)):
        for j in range(i+1, len(images)):
            if (i,j) in processed_pairs:
                continue
                
            if i in signatures and j in signatures and signatures[i] - signatures[j] < 10:
                duplicates.append((i,j))
                processed_pairs.add((i,j))
                print(f"[MATCH] pHash: {os.path.basename(valid_paths[i])} ↔ {os.path.basename(valid_paths[j])}")
    
    # SIFT comparison for remaining images
    print("[STATUS] Running SIFT comparison...")
    sift = cv2.SIFT_create()
    for i in range(len(images)):
        for j in range(i+1, len(images)):
            if (i,j) in processed_pairs:
                continue
                
            try:
                img1 = cv2.cvtColor(images[i], cv2.COLOR_RGB2GRAY)
                img2 = cv2.cvtColor(images[j], cv2.COLOR_RGB2GRAY)
                
                kp1, des1 = sift.detectAndCompute(img1, None)
                kp2, des2 = sift.detectAndCompute(img2, None)
                
                if des1 is None or des2 is None:
                    continue
                
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(des1, des2, k=2)
                
                good = []
                for m,n in matches:
                    if m.distance < 0.75*n.distance:
                        good.append(m)
                
                similarity = len(good) / min(len(kp1), len(kp2)) if min(len(kp1), len(kp2)) > 0 else 0
                if similarity > SIFT_THRESHOLD:
                    duplicates.append((i,j))
                    processed_pairs.add((i,j))
                    print(f"[MATCH] SIFT: {os.path.basename(valid_paths[i])} ↔ {os.path.basename(valid_paths[j])} (similarity: {similarity:.2f})")
            except Exception as e:
                print(f"[WARNING] Error comparing images: {str(e)}")
                continue
    
    return [(valid_paths[i], valid_paths[j]) for i,j in duplicates]

def save_duplicates_to_drive(service, duplicates, image_paths, parent_id):
    """Save duplicate pairs to Google Drive with robust error handling"""
    print("\n[STATUS] Saving duplicates to Google Drive...")
    
    folder_id = None
    max_retries = 3
    retry_delay = 5
    
    # Try to create folder with retries
    for attempt in range(max_retries):
        try:
            folder_metadata = {
                'name': DUPLICATES_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            print("[SUCCESS] Created duplicates folder")
            break
        except HttpError as e:
            if attempt < max_retries - 1:
                print(f"[RETRY] Folder creation failed (attempt {attempt+1}), retrying...")
                time.sleep(retry_delay)
            else:
                print("[WARNING] Failed to create folder after multiple attempts")
    
    # If still no folder, try to find existing
    if not folder_id:
        try:
            existing_query = f"name='{DUPLICATES_FOLDER_NAME}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'"
            existing = service.files().list(q=existing_query, fields="files(id)").execute().get('files', [])
            if existing:
                folder_id = existing[0]['id']
                print("[SUCCESS] Found existing duplicates folder")
            else:
                print("[ERROR] Could not create or find duplicates folder")
                return 0
        except Exception as e:
            print(f"[ERROR] Failed to find existing folder: {str(e)}")
            return 0
    
    # Upload duplicates
    uploaded_count = 0
    total_pairs = min(len(duplicates), MAX_DUPLICATES_TO_UPLOAD)
    
    print(f"\n[STATUS] Uploading {total_pairs} duplicate pairs:")
    for pair_num, (path1, path2) in enumerate(duplicates[:MAX_DUPLICATES_TO_UPLOAD], 1):
        try:
            print(f"  Pair {pair_num}/{total_pairs}: {os.path.basename(path1)} and {os.path.basename(path2)}")
            
            for img_num, path in enumerate([path1, path2], 1):
                file_metadata = {
                    'name': f"pair{pair_num}_dup{img_num}_{os.path.basename(path)}",
                    'parents': [folder_id]
                }
                
                media = MediaFileUpload(
                    path,
                    mimetype='image/jpeg',
                    resumable=True
                )
                
                # Upload with retry
                for upload_attempt in range(2):
                    try:
                        service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id'
                        ).execute()
                        break
                    except Exception as e:
                        if upload_attempt == 0:
                            print(f"    [RETRY] Upload failed, retrying...")
                            time.sleep(2)
                        else:
                            raise
            
            uploaded_count += 1
        except Exception as e:
            print(f"  [ERROR] Failed to upload pair {pair_num}: {str(e)}")
            continue
    
    print(f"\n[RESULT] Successfully uploaded {uploaded_count} duplicate pairs")
    return uploaded_count

def main(access_token, temp_dir):
    """Main deduplication function"""
    try:
        print("\n=== IMAGE DEDUPLICATION TOOL ===")
        
        # Authenticate
        print("\n[1/6] Authenticating with Google Drive API...")
        creds = Credentials(access_token)
        service = build('drive', 'v3', credentials=creds, static_discovery=False)
        print("[SUCCESS] Authentication successful")
        
        # Find target folder
        print("\n[2/6] Locating 'Final Year Project' folder...")
        folder_query = "name='Final Year Project' and mimeType='application/vnd.google-apps.folder'"
        folders = service.files().list(q=folder_query, fields="files(id,name)").execute().get('files', [])
        
        if not folders:
            raise Exception("'Final Year Project' folder not found")
        
        parent_id = folders[0]['id']
        print("[SUCCESS] Found parent folder")
        
        # Find images dataset folder
        print("\n[3/6] Locating 'imagedatasetAdi' folder...")
        dataset_query = f"name='imagedatasetAdi' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        dataset_folders = service.files().list(q=dataset_query, fields="files(id,name)").execute().get('files', [])
        
        if not dataset_folders:
            raise Exception("'imagedatasetAdi' folder not found")
        
        dataset_id = dataset_folders[0]['id']
        print("[SUCCESS] Found dataset folder")
        
        # List all images
        print("\n[4/6] Scanning for images...")
        images = service.files().list(
            q=f"'{dataset_id}' in parents and (mimeType contains 'image/' or mimeType contains 'application/octet-stream')",
            fields="files(id,name,mimeType)",
            pageSize=1000
        ).execute().get('files', [])
        
        if not images:
            raise Exception("No images found in the dataset folder")
        
        print(f"[SUCCESS] Found {len(images)} images")
        
        # Create temp directory
        print("\n[5/6] Preparing temporary directory...")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download images
        print("\n[STATUS] Downloading images:")
        image_paths = []
        for idx, img in enumerate(images):
            try:
                img_path = os.path.join(temp_dir, img['name'])
                request = service.files().get_media(fileId=img['id'])
                
                with open(img_path, 'wb') as f:
                    f.write(request.execute())
                
                # Verify image
                try:
                    with Image.open(img_path) as test_img:
                        test_img.verify()
                    image_paths.append(img_path)
                    print(f"  Downloaded {idx+1}/{len(images)}: {img['name']}")
                except:
                    print(f"  [WARNING] Skipping corrupted image: {img['name']}")
                    os.remove(img_path)
            except Exception as e:
                print(f"  [ERROR] Failed to download {img['name']}: {str(e)}")
                continue
        
        if not image_paths:
            raise Exception("No valid images could be processed")
        
        print(f"\n[SUCCESS] Downloaded {len(image_paths)} valid images")
        
        # Find duplicates
        print("\n[6/6] Finding duplicates...")
        duplicates = find_duplicates(image_paths)
        
        if duplicates:
            print(f"\n[RESULT] Found {len(duplicates)} duplicate pairs")
            uploaded_count = save_duplicates_to_drive(service, duplicates, image_paths, dataset_id)
            print(f"[SUMMARY] Uploaded {uploaded_count} duplicate pairs to Drive")
        else:
            print("\n[RESULT] No duplicates found")
        
        return len(duplicates)
        
    except Exception as e:
        print(f"\n[ERROR] Deduplication failed: {str(e)}")
        raise
    finally:
        # Clean up temp directory
        if 'temp_dir' in locals():
            try:
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"[WARNING] Could not delete {file_path}: {str(e)}")
                print("[STATUS] Cleaned up temporary files")
            except Exception as e:
                print(f"[WARNING] Temp directory cleanup failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python deduplication.py <access_token> <temp_dir>")
        sys.exit(1)
    
    try:
        duplicates_count = main(sys.argv[1], sys.argv[2])
        print("\n=== PROCESS COMPLETED ===")
        print(f"Total duplicate pairs found: {duplicates_count}")
        sys.exit(0)
    except Exception as e:
        print("\n=== PROCESS FAILED ===")
        print(f"Error: {str(e)}")
        sys.exit(1)