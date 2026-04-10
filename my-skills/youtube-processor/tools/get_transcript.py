#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Simple tool that extracts transcripts from YouTube videos.
Claude does the summarization directly (no API key needed here).

Usage:
    python3 get_transcript.py --url "https://youtube.com/watch?v=..."
    python3 get_transcript.py --url "..." --json
    python3 get_transcript.py --url "..." --timestamps  # Include timestamps for key moments
"""

import argparse
import json
import sys
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'embed\/([0-9A-Za-z_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")


def format_timestamp(seconds: float) -> str:
    """Convert seconds to [MM:SS] or [H:MM:SS] format."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"[{hours}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes}:{secs:02d}]"


def get_transcript_raw(video_id: str) -> tuple:
    """
    Fetch raw transcript data from YouTube video with timing info.
    Returns: (transcript_items, language_code)
    Each item has: text, start (seconds), duration (seconds)
    """
    ytt_api = YouTubeTranscriptApi()

    try:
        transcript_data = ytt_api.fetch(video_id, languages=['en'])
        return transcript_data, 'en'
    except Exception:
        # Fall back to any available transcript
        transcript_list = ytt_api.list(video_id)
        for transcript in transcript_list:
            transcript_data = transcript.fetch()
            return transcript_data, transcript.language_code

    raise ValueError("No transcript found")


def get_transcript(video_id: str) -> tuple:
    """Fetch transcript from YouTube video (text only)."""
    transcript_data, lang = get_transcript_raw(video_id)
    full_text = " ".join([item.text for item in transcript_data])
    return full_text, lang


def get_transcript_with_timestamps(video_id: str) -> tuple:
    """
    Fetch transcript with timestamps for key moment identification.
    Returns: (timestamped_segments, language_code)
    Each segment is: {"text": str, "timestamp": "[MM:SS]", "start": float}
    """
    transcript_data, lang = get_transcript_raw(video_id)

    segments = []
    for item in transcript_data:
        segments.append({
            "text": item.text,
            "timestamp": format_timestamp(item.start),
            "start": item.start
        })

    return segments, lang


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube transcripts")
    parser.add_argument("--url", "-u", required=True, help="YouTube video URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--timestamps", "-t", action="store_true",
                        help="Include timestamps for each segment (for key moment identification)")

    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)

        if args.timestamps:
            # Get timestamped segments for key moment identification
            segments, lang = get_transcript_with_timestamps(video_id)
            full_text = " ".join([s["text"] for s in segments])

            if args.json:
                print(json.dumps({
                    "success": True,
                    "video_id": video_id,
                    "language": lang,
                    "segments": segments,
                    "transcript": full_text,
                    "char_count": len(full_text),
                    "segment_count": len(segments)
                }, indent=2))
            else:
                print(f"Video ID: {video_id}")
                print(f"Language: {lang}")
                print(f"Segments: {len(segments)}")
                print(f"\n--- TIMESTAMPED TRANSCRIPT ---\n")
                for seg in segments:
                    print(f"{seg['timestamp']} {seg['text']}")
        else:
            # Standard text-only transcript
            transcript, lang = get_transcript(video_id)

            if args.json:
                print(json.dumps({
                    "success": True,
                    "video_id": video_id,
                    "language": lang,
                    "transcript": transcript,
                    "char_count": len(transcript)
                }, indent=2))
            else:
                print(f"Video ID: {video_id}")
                print(f"Language: {lang}")
                print(f"Length: {len(transcript)} characters")
                print(f"\n--- TRANSCRIPT ---\n")
                print(transcript)

    except TranscriptsDisabled:
        error = "Transcripts are disabled for this video"
        if args.json:
            print(json.dumps({"success": False, "error": error}))
        else:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except NoTranscriptFound:
        error = "No transcript found for this video"
        if args.json:
            print(json.dumps({"success": False, "error": error}))
        else:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except VideoUnavailable:
        error = "Video is unavailable or does not exist"
        if args.json:
            print(json.dumps({"success": False, "error": error}))
        else:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
