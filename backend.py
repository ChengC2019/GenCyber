from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RequestBody(BaseModel):
    text: str

@app.post("/generate-asl-video")
def generate_asl_video(body: RequestBody):
    return {
        "video_url": "https://www.w3schools.com/html/mov_bbb.mp4"
    }