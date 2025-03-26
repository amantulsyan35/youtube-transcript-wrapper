from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import uvicorn

app = FastAPI(
    title="YouTube Transcript API",
    description="Retrieve transcripts for YouTube videos",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/transcript/{video_id}")
async def get_transcript(
    video_id: str, 
    language: str = 'en'
):
    """
    Retrieve transcript for a given YouTube video
    
    :param video_id: YouTube video ID
    :param language: Language code for the transcript (default is 'en')
    :return: Transcript data
    """
    try:
        # Create YouTubeTranscriptApi instance
        ytt_api = YouTubeTranscriptApi()
        
        # Fetch transcript
        transcript = ytt_api.fetch(video_id, languages=[language])
        
        # Convert to raw data and return
        return {
            "video_id": video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "transcript": transcript.to_raw_data()
        }
    
    except Exception as e:
        # Handle potential errors
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/transcripts/{video_id}")
async def list_transcripts(video_id: str):
    """
    List available transcripts for a given YouTube video
    
    :param video_id: YouTube video ID
    :return: List of available transcripts
    """
    try:
        # Create YouTubeTranscriptApi instance
        ytt_api = YouTubeTranscriptApi()
        
        # List available transcripts
        transcript_list = ytt_api.list(video_id)
        
        # Convert to list of dictionaries with metadata
        available_transcripts = [
            {
                'language': t.language,
                'language_code': t.language_code,
                'is_generated': t.is_generated,
                'is_translatable': t.is_translatable,
                'translation_languages': t.translation_languages
            } for t in transcript_list
        ]
        
        return available_transcripts
    
    except Exception as e:
        # Handle potential errors
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/")
async def root():
    """
    Root endpoint with basic API information
    """
    return {
        "message": "YouTube Transcript API",
        "endpoints": [
            "/transcript/{video_id}",
            "/transcripts/{video_id}"
        ]
    }

# If you want to run the server directly from this file
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)