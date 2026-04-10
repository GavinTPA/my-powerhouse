#!/usr/bin/env python3
"""
Instagram Reel Poster
=====================
Posts Reels (short-form video) to Instagram via Graph API.

Workflow:
1. Upload video to Vercel Blob (get public URL)
2. Create REELS container
3. Wait for video processing
4. Publish reel
5. Clean up Blob storage

Requires:
- BLOB_READ_WRITE_TOKEN environment variable
- ~/.config/instagram-poster.yaml with access_token and instagram_user_id

Usage:
    python3 post_reel.py --video ~/Downloads/reel-folder/final.mp4 --caption "Your caption here"
    python3 post_reel.py --video final.mp4 --caption "Caption" --thumb-offset 3000
    python3 post_reel.py --video final.mp4 --caption "Caption" --cover ~/Downloads/cover.jpg
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime

from token_utils import ensure_fresh_token, load_config

# Instagram Graph API base
GRAPH_API_BASE = "https://graph.instagram.com/v21.0"


def upload_video_to_blob(video_path: Path) -> str:
    """
    Upload video to Vercel Blob storage.
    Returns public URL.
    """
    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        raise EnvironmentError("BLOB_READ_WRITE_TOKEN environment variable not set")

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"reels/{timestamp}_{video_path.name}"

    # Read video
    with open(video_path, "rb") as f:
        video_data = f.read()

    # Determine content type from extension
    suffix = video_path.suffix.lower()
    content_type = "video/mp4" if suffix == ".mp4" else "video/quicktime"

    # Upload to Vercel Blob
    response = requests.put(
        f"https://blob.vercel-storage.com/{filename}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
            "x-api-version": "7",
        },
        data=video_data
    )

    if response.status_code != 200:
        raise Exception(f"Blob upload failed: {response.status_code} - {response.text}")

    result = response.json()
    return result.get("url")


def upload_image_to_blob(image_path: Path) -> str:
    """
    Upload image to Vercel Blob storage.
    Returns public URL.
    """
    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        raise EnvironmentError("BLOB_READ_WRITE_TOKEN environment variable not set")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"reel-covers/{timestamp}_{image_path.name}"

    with open(image_path, "rb") as f:
        image_data = f.read()

    # Determine content type from extension
    suffix = image_path.suffix.lower()
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }
    content_type = content_types.get(suffix, "image/jpeg")

    response = requests.put(
        f"https://blob.vercel-storage.com/{filename}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
            "x-api-version": "7",
        },
        data=image_data
    )

    if response.status_code != 200:
        raise Exception(f"Cover image upload failed: {response.status_code} - {response.text}")

    result = response.json()
    return result.get("url")


def delete_from_blob(url: str) -> bool:
    """Delete video from Vercel Blob storage."""
    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        return False

    try:
        response = requests.delete(
            "https://blob.vercel-storage.com",
            headers={
                "Authorization": f"Bearer {token}",
                "x-api-version": "7",
            },
            json={"urls": [url]}
        )
        return response.status_code == 200
    except Exception:
        return False


def create_reel_container(user_id: str, access_token: str, video_url: str, caption: str,
                          thumb_offset: int = None, cover_url: str = None) -> str:
    """
    Create a REELS media container.
    Returns container ID.

    Optional params:
    - thumb_offset: Milliseconds into the video to use as cover frame
    - cover_url: Public URL of a custom cover image
    """
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true",  # Post to both Reels tab and feed
        "access_token": access_token,
    }

    if thumb_offset is not None:
        params["thumb_offset"] = str(thumb_offset)

    if cover_url is not None:
        params["cover_url"] = cover_url

    response = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/media",
        data=params
    )

    if response.status_code != 200:
        raise Exception(f"Reel container creation failed: {response.json()}")

    return response.json()["id"]


def wait_for_container(container_id: str, access_token: str, max_attempts: int = 60) -> bool:
    """
    Poll container until status is FINISHED.
    Video processing takes longer than images - default 60 attempts.
    Returns True if successful.
    """
    for attempt in range(max_attempts):
        response = requests.get(
            f"{GRAPH_API_BASE}/{container_id}",
            params={
                "fields": "status_code",
                "access_token": access_token
            }
        )

        if response.status_code != 200:
            print(f"  Status check failed: {response.json()}", file=sys.stderr)
            return False

        status = response.json().get("status_code")

        if status == "FINISHED":
            return True
        elif status == "ERROR":
            print(f"  Container error: {response.json()}", file=sys.stderr)
            return False

        # Wait with exponential backoff (cap at 30 seconds)
        wait_time = min(2 ** min(attempt, 4), 30)  # 2, 4, 8, 16, 30, 30, 30...
        print(f"  Container status: {status}, waiting {wait_time}s...", file=sys.stderr)
        time.sleep(wait_time)

    return False


def publish_media(user_id: str, access_token: str, creation_id: str) -> str:
    """
    Publish the media container.
    Returns the media ID of the published reel.
    """
    response = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": access_token
        }
    )

    if response.status_code != 200:
        raise Exception(f"Publish failed: {response.json()}")

    return response.json()["id"]


def get_permalink(media_id: str, access_token: str) -> str:
    """Get the Instagram permalink for a published reel."""
    response = requests.get(
        f"{GRAPH_API_BASE}/{media_id}",
        params={
            "fields": "permalink",
            "access_token": access_token
        }
    )

    if response.status_code == 200:
        return response.json().get("permalink", "")
    return ""


def post_reel(video_path: Path, caption: str, thumb_offset: int = None,
              cover_path: Path = None) -> dict:
    """
    Main function to post a Reel to Instagram.

    Args:
        video_path: Path to video file (MP4 or MOV)
        caption: Caption text for the Reel
        thumb_offset: Milliseconds into video for cover frame (optional)
        cover_path: Path to custom cover image to upload (optional)

    Returns dict with:
    - success: bool
    - media_id: str (if success)
    - permalink: str (if success)
    - error: str (if failure)
    """
    # Ensure token is fresh (auto-refresh if expiring soon)
    access_token = ensure_fresh_token()

    # Load config for user_id
    config = load_config()
    user_id = config["instagram_user_id"]

    # Validate video file
    if not video_path.exists():
        return {"success": False, "error": f"Video not found: {video_path}"}

    suffix = video_path.suffix.lower()
    if suffix not in [".mp4", ".mov"]:
        return {"success": False, "error": f"Unsupported video format: {suffix}. Use MP4 or MOV."}

    # Check file size (Instagram limit is ~300MB for Reels)
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 300:
        return {"success": False, "error": f"Video too large: {file_size_mb:.1f}MB (max 300MB)"}

    # Validate cover image if provided
    if cover_path is not None:
        if not cover_path.exists():
            return {"success": False, "error": f"Cover image not found: {cover_path}"}
        cover_suffix = cover_path.suffix.lower()
        if cover_suffix not in [".jpg", ".jpeg", ".png"]:
            return {"success": False, "error": f"Unsupported cover format: {cover_suffix}. Use JPG or PNG."}

    print(f"Video: {video_path.name} ({file_size_mb:.1f}MB)", file=sys.stderr)
    if thumb_offset is not None:
        print(f"Thumb offset: {thumb_offset}ms", file=sys.stderr)
    if cover_path is not None:
        print(f"Cover image: {cover_path.name}", file=sys.stderr)

    blob_url = None
    cover_blob_url = None

    try:
        # Step 1: Upload video to Blob
        print("Uploading video to Vercel Blob...", file=sys.stderr)
        blob_url = upload_video_to_blob(video_path)
        print(f"  -> {blob_url[:60]}...", file=sys.stderr)

        # Step 1b: Upload cover image to Blob (if provided)
        if cover_path is not None:
            print("Uploading cover image to Vercel Blob...", file=sys.stderr)
            cover_blob_url = upload_image_to_blob(cover_path)
            print(f"  -> {cover_blob_url[:60]}...", file=sys.stderr)

        # Step 2: Create REELS container
        print("Creating Reel container...", file=sys.stderr)
        container_id = create_reel_container(
            user_id, access_token, blob_url, caption,
            thumb_offset=thumb_offset,
            cover_url=cover_blob_url,
        )
        print(f"  Container ID: {container_id}", file=sys.stderr)

        # Step 3: Wait for video processing
        print("Waiting for video processing...", file=sys.stderr)
        if not wait_for_container(container_id, access_token):
            return {"success": False, "error": "Video container failed to process"}

        # Step 4: Publish
        print("Publishing Reel...", file=sys.stderr)
        media_id = publish_media(user_id, access_token, container_id)
        print(f"  Media ID: {media_id}", file=sys.stderr)

        # Get permalink
        permalink = get_permalink(media_id, access_token)

        return {
            "success": True,
            "media_id": media_id,
            "permalink": permalink
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        # Cleanup: Delete video from Blob
        if blob_url:
            print("Cleaning up Blob storage...", file=sys.stderr)
            delete_from_blob(blob_url)
        # Cleanup: Delete cover image from Blob
        if cover_blob_url:
            print("Cleaning up cover image from Blob...", file=sys.stderr)
            delete_from_blob(cover_blob_url)


def main():
    parser = argparse.ArgumentParser(description="Post Reel to Instagram")
    parser.add_argument("--video", required=True, help="Path to video file (MP4 or MOV)")
    parser.add_argument("--caption", required=True, help="Caption for the Instagram Reel")
    parser.add_argument("--thumb-offset", type=int, default=None,
                        help="Milliseconds into the video to use as cover frame (e.g. 3000 for 3s)")
    parser.add_argument("--cover", default=None,
                        help="Path to custom cover image (JPG or PNG). Uploaded to Vercel Blob and passed as cover_url.")

    args = parser.parse_args()

    video_path = Path(args.video).expanduser()
    if not video_path.exists():
        print(f"Error: Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    cover_path = None
    if args.cover:
        cover_path = Path(args.cover).expanduser()
        if not cover_path.exists():
            print(f"Error: Cover image not found: {cover_path}", file=sys.stderr)
            sys.exit(1)

    result = post_reel(video_path, args.caption, thumb_offset=args.thumb_offset,
                       cover_path=cover_path)

    # Output result as JSON
    print(json.dumps(result, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
