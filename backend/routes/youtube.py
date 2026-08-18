import re

from fastapi import Depends, HTTPException

from youtube_transcript_api import YouTubeTranscriptApi

from ..core.app import app
from ..schemas.models import YouTubeRequest
from ..services.auth import current_user


def extract_youtube_video_id(url: str):
    """Extract a YouTube video ID from common YouTube URL formats."""
    patterns = [
        r"(?:youtube\.com/watch\?v=)([^&]+)",
        r"(?:youtu\.be/)([^?&]+)",
        r"(?:youtube\.com/shorts/)([^?&]+)",
        r"(?:youtube\.com/embed/)([^?&]+)",
        r"(?:youtube\.com/live/)([^?&]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


@app.post("/api/youtube/extract")
def extract_youtube(
    req: YouTubeRequest,
    user=Depends(current_user),
):
    """Extract an accessible YouTube transcript and return it as source_text."""
    video_id = extract_youtube_video_id(req.url.strip())

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid YouTube video URL.",
        )

    try:
        print("YOUTUBE VIDEO ID:", video_id)

        transcript = YouTubeTranscriptApi().fetch(video_id)

        text_parts = []

        for item in transcript:
            if hasattr(item, "text"):
                value = item.text
            elif isinstance(item, dict):
                value = item.get("text", "")
            else:
                value = str(item)

            if value and str(value).strip():
                text_parts.append(str(value).strip())

        text = " ".join(text_parts).strip()

        if not text:
            raise HTTPException(
                status_code=404,
                detail="No transcript/captions were found for this YouTube video.",
            )

        print(
            "YOUTUBE TRANSCRIPT EXTRACTED:",
            len(text),
            "characters",
        )

        return {
            "success": True,
            "video_id": video_id,
            "title": f"YouTube Video ({video_id})",
            "text": text,
            "source_text": text,
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            "YOUTUBE TRANSCRIPT ERROR:",
            repr(e),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not extract the YouTube transcript. "
                "Make sure the video is accessible and has captions/transcript. "
                f"Error: {str(e)}"
            ),
        )
