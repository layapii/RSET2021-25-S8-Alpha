from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
import requests

from ..database import conn, cursor
from .. import schemas, oauth2
from .. import extractor, nlp, generator

router = APIRouter(
    prefix="/news",
    tags=['News'] # for documentation
)


@router.post("/image", status_code=status.HTTP_201_CREATED)
def image_to_text(image: UploadFile = File(...)):
    
    try:
        article = extractor.extract(image)
        print(f"\nARTICLE:\n{article}")

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    
    return JSONResponse(content={"text": article}, status_code=status.HTTP_200_OK)


@router.post("/text", status_code=status.HTTP_201_CREATED)
def text_to_reel(input_data: schemas.TextInput, current_user: int = Depends(oauth2.get_current_user)):
        
    print("\nStarted!!!")
    article = input_data.text
    targetLanguage = input_data.language

    # SUMMARIZER
    summary = nlp.full_summarize(article)
    print(f"\nSUMMARY:\n{summary}")

    # CLASSIFIER
    category = nlp.full_classify(summary)
    print(f"\nCATEGORY:\n{category}")

    #vid gen
    generator.generate(summary, category, targetLanguage)

    # upload to cloudinary
    data = {'upload_preset': 'upload_reels'}
    files = {'file': open('outputs/reel.mp4', 'rb')}
    response = requests.post('https://api.cloudinary.com/v1_1/news-to-reel/video/upload', data=data, files=files)
    reel_url = response.json()['secure_url']
    print(f"REEL_URL:\n{reel_url}")

    # insert data into table
    try:
        cursor.execute("""INSERT INTO reels (owner_id, article, lang, summary, category, reel_url) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""", (current_user, article, targetLanguage, summary, category, reel_url))
        new_reel = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="server error")

    return JSONResponse(content={"reel_url": reel_url}, status_code=status.HTTP_200_OK)


@router.post("/history", status_code=status.HTTP_200_OK)
def fetch_reels(filters: schemas.Filter, current_user: int = Depends(oauth2.get_current_user)):
    try:
        query = "SELECT * FROM reels WHERE owner_id = %s"
        params = [current_user]

        query += " AND lang = ANY(%s)"
        params.append(filters.languages)
        
        if filters.category:
            query += " AND category = %s"
            params.append(filters.category)

        cursor.execute(query, params)
        reels = cursor.fetchall()

        reels = jsonable_encoder(reels)

    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    
    return JSONResponse(content={"reels": reels}, status_code=status.HTTP_200_OK)

# # handled in frontend
# @router.get("/demo", status_code=status.HTTP_201_CREATED)
# def demo(language: str):
#     demo_reel = f'outputs/demo_{language}.mp4'
#     return FileResponse(demo_reel, media_type="video/mp4")