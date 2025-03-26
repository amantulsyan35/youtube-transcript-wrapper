from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import uvicorn
from proxy_manager import ProxyManager

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Transcript API",
    description="Retrieve transcripts for YouTube videos",
    version="1.0.0"
)

# Initialize proxy manager
proxy_manager = ProxyManager()

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
    # Get proxies from the proxy manager
    proxies = proxy_manager.get_proxy()
    
    for attempt in range(3):  # Try up to 3 times with different proxies
        try:
            # Get transcript using proxies
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=[language],
                proxies=proxies
            )
            
            # Return the transcript data
            return {
                "video_id": video_id,
                "language": language,
                "transcript": transcript_list
            }
        
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # These errors mean the video doesn't have transcripts, no need to retry
            raise HTTPException(status_code=404, detail=str(e))
            
        except Exception as e:
            if "IP" in str(e) and attempt < 2:
                # If it's an IP block and we haven't exhausted our attempts,
                # get a new proxy and try again
                proxies = proxy_manager.get_proxy()
                continue
            else:
                # On the last attempt or for other errors, raise the exception
                raise HTTPException(status_code=404, detail=str(e))

@app.get("/transcripts/{video_id}")
async def list_transcripts(video_id: str):
    """
    List available transcripts for a given YouTube video
    
    :param video_id: YouTube video ID
    :return: List of available transcripts
    """
    # Get proxies from the proxy manager
    proxies = proxy_manager.get_proxy()
    
    for attempt in range(3):  # Try up to 3 times with different proxies
        try:
            # List available transcripts with proxies
            transcript_list = YouTubeTranscriptApi.list_transcripts(
                video_id,
                proxies=proxies
            )
            
            # Convert to list of dictionaries with metadata
            available_transcripts = [
                {
                    'language': t.language,
                    'language_code': t.language_code,
                    'is_generated': t.is_generated,
                    'is_translatable': t.is_translatable,
                    'translation_languages': [
                        {'language': lang.language, 'language_code': lang.language_code}
                        for lang in t.translation_languages
                    ] if hasattr(t, 'translation_languages') else []
                } for t in transcript_list
            ]
            
            return available_transcripts
        
        except Exception as e:
            if "IP" in str(e) and attempt < 2:
                # If it's an IP block and we haven't exhausted our attempts,
                # get a new proxy and try again
                proxies = proxy_manager.get_proxy()
                continue
            else:
                # On the last attempt or for other errors, raise the exception
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