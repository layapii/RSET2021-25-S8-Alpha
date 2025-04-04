from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import user, news

# uvicorn app.main:app --reload --host 0.0.0.0    ##fetch('http://localhost:8000/').then(res => res.json()).then(console.log)
# npm run dev -- --host

app = FastAPI()

origins = ["*"]

app.add_middleware( 
    CORSMiddleware, #middleware runs before every request
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(news.router)

@app.get("/")
def root():
    return {"message":"check out news-to-reel/docs for api documentation"}
