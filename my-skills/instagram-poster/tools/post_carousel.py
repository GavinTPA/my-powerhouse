#!/usr/bin/env python3
"""
Instagram Carousel Poster
=========================
Posts carousel images to Instagram via Graph API.

Workflow:
1. Upload images to Vercel Blob (get public URLs)
2. Create child containers for each image
3. Create carousel container
4. Publish carousel
5. Clean up Blob storage

Requires:
- BLOB_READ_WRITE_TOKEN environment variable
- ~/.config/instagram-poster.yaml with access_token and instagram_user_id

Usage:
    python3 post_carousel.py --folder ~/Downloads/carousel260114 --caption "Your caption here"
"""

import os
import sys
import time
import json
import argparse
import requests
import yaml
from pathlib import Path
from datetime import datetime

from token_utils import ensure_fresh_token, load_config

# Template file location (relative to this script)
TEMPLATES_FILE = Path(__file__).parent.parent / "resources" / "caption-templates.yaml"

# Instagram Graph API base
GRAPH_API_BASE = "https://graph.instagram.com/v21.0"


def load_templates() -> dict:
    """Load caption templates from YAML file."""
    if not TEMPLATES_FILE.exists():
        return {}

    with open(TEMPLATES_FILE, "r") as f:
        data = yaml.safe_load(f)

    return data.get("templates", {})


def list_templates() -> list:
    """Return list of available template names."""
    templates = load_templates()
    return list(templates.keys())


def render_template(template_name: str, title: str = "", topic: str = "", cta: str = "") -> str:
    """
    Render a caption template with variable substitution.

    Args:
        template_name: Name of the template (e.g., 'carousel', 'educational')
        title: Main headline or topic title
        topic: Subject matter / niche area (used in hashtags)
        cta: Call to action (uses template default if not provided)

    Returns:
        Rendered caption string

    Raises:
        ValueError: If template name not found
    """
    templates = load_templates()

    if template_name not in templates:
        available = ", ".join(templates.keys())
        raise ValueError(f"Template '{template_name}' not found. Available: {available}")

    template = templates[template_name]
    structure = template.get("structure", "")
    default_cta = template.get("default_cta", "")

    # Use default CTA if none provided
    if not cta:
        cta = default_cta

    # Clean up topic for hashtag use (lowercase, no spaces)
    topic_hashtag = topic.lower().replace(" ", "").replace("-", "") if topic else "business"

    # Perform variable substitution
    caption = structure.format(
        title=title,
        topic=topic_hashtag,
        cta=cta
    )

    return caption.strip()


def upload_to_blob(image_path: Path) -> str:
    """
    Upload image to Vercel Blob storage.
    Returns public URL.
    """
    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        raise EnvironmentError("BLOB_READ_WRITE_TOKEN environment variable not set")

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"carousel/{timestamp}_{image_path.name}"

    # Read image
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Upload to Vercel Blob
    # Using the Vercel Blob REST API
    response = requests.put(
        f"https://blob.vercel-storage.com/{filename}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "image/png",
            "x-api-version": "7",
        },
        data=image_data
    )

    if response.status_code != 200:
        raise Exception(f"Blob upload failed: {response.status_code} - {response.text}")

    result = response.json()
    return result.get("url")


def delete_from_blob(url: str) -> bool:
    """Delete image from Vercel Blob storage."""
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


def create_media_container(user_id: str, access_token: str, image_url: str, is_carousel_item: bool = True) -> str:
    """
    Create a media container for an image.
    Returns container ID.
    """
    params = {
        "image_url": image_url,
        "access_token": access_token,
    }

    if is_carousel_item:
        params["is_carousel_item"] = "true"

    response = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/media",
        data=params
    )

    if response.status_code != 200:
        raise Exception(f"Container creation failed: {response.json()}")

    return response.json()["id"]


def wait_for_container(container_id: str, access_token: str, max_attempts: int = 30) -> bool:
    """
    Poll container until status is FINISHED.
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

        # Wait with exponential backoff
        wait_time = min(2 ** attempt, 30)
        print(f"  Container status: {status}, waiting {wait_time}s...", file=sys.stderr)
        time.sleep(wait_time)

    return False


def create_carousel_container(user_id: str, access_token: str, children_ids: list, caption: str) -> str:
    """
    Create carousel container from child containers.
    Returns carousel container ID.
    """
    response = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/media",
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": access_token
        }
    )

    if response.status_code != 200:
        raise Exception(f"Carousel creation failed: {response.json()}")

    return response.json()["id"]


def publish_media(user_id: str, access_token: str, creation_id: str) -> str:
    """
    Publish the media container.
    Returns the media ID of the published post.
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
    """Get the Instagram permalink for a published post."""
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


def post_carousel(folder_path: Path, caption: str) -> dict:
    """
    Main function to post a carousel to Instagram.

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

    # Find images in folder
    images = sorted(folder_path.glob("*.png"))
    if not images:
        images = sorted(folder_path.glob("*.jpg"))

    if len(images) < 2:
        return {"success": False, "error": "Carousel requires at least 2 images"}
    if len(images) > 10:
        return {"success": False, "error": "Carousel maximum is 10 images"}

    print(f"Found {len(images)} images to post", file=sys.stderr)

    blob_urls = []
    children_ids = []

    try:
        # Step 1: Upload all images to Blob
        print("Uploading images to Vercel Blob...", file=sys.stderr)
        for i, img_path in enumerate(images, 1):
            print(f"  [{i}/{len(images)}] {img_path.name}", file=sys.stderr)
            url = upload_to_blob(img_path)
            blob_urls.append(url)
            print(f"    -> {url[:60]}...", file=sys.stderr)

        # Step 2: Create child containers
        print("Creating media containers...", file=sys.stderr)
        for i, url in enumerate(blob_urls, 1):
            print(f"  [{i}/{len(blob_urls)}] Creating container...", file=sys.stderr)
            container_id = create_media_container(user_id, access_token, url)
            print(f"    Container ID: {container_id}", file=sys.stderr)

            # Wait for processing
            if not wait_for_container(container_id, access_token):
                return {"success": False, "error": f"Container {i} failed to process"}

            children_ids.append(container_id)

        # Step 3: Create carousel container
        print("Creating carousel container...", file=sys.stderr)
        carousel_id = create_carousel_container(user_id, access_token, children_ids, caption)
        print(f"  Carousel ID: {carousel_id}", file=sys.stderr)

        # Wait for carousel processing
        if not wait_for_container(carousel_id, access_token):
            return {"success": False, "error": "Carousel container failed to process"}

        # Step 4: Publish
        print("Publishing carousel...", file=sys.stderr)
        media_id = publish_media(user_id, access_token, carousel_id)
        print(f"  Media ID: {media_id}", file=sys.stderr)

        # Get permalink
        permalink = get_permalink(media_id, access_token)

        return {
            "success": True,
            "media_id": media_id,
            "permalink": permalink,
            "images_posted": len(images)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        # Cleanup: Delete images from Blob
        print("Cleaning up Blob storage...", file=sys.stderr)
        for url in blob_urls:
            delete_from_blob(url)


def main():
    parser = argparse.ArgumentParser(
        description="Post carousel to Instagram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With direct caption
  python3 post_carousel.py --folder ~/Downloads/carousel --caption "Your caption here"

  # With template
  python3 post_carousel.py --folder ~/Downloads/carousel --template carousel --title "5 Things I Wish I Knew"

  # With template and custom CTA
  python3 post_carousel.py --folder ~/Downloads/carousel --template educational --title "Build Faster" --topic "SaaS" --cta "DM me 'BUILD' to learn more"

  # List available templates
  python3 post_carousel.py --list-templates
        """
    )
    parser.add_argument("--folder", help="Path to carousel images folder")
    parser.add_argument("--caption", help="Caption for the Instagram post (use this OR --template)")

    # Template options
    parser.add_argument("--template", help="Name of caption template to use (e.g., carousel, educational, promotional)")
    parser.add_argument("--title", help="Title/headline for template variable {title}")
    parser.add_argument("--topic", help="Topic for template variable {topic} (used in hashtags)")
    parser.add_argument("--cta", help="Call to action for template variable {cta} (uses template default if omitted)")
    parser.add_argument("--list-templates", action="store_true", help="List available caption templates and exit")

    args = parser.parse_args()

    # Handle --list-templates
    if args.list_templates:
        templates = load_templates()
        if not templates:
            print("No templates found.", file=sys.stderr)
            sys.exit(1)

        print("Available caption templates:\n")
        for name, template in templates.items():
            desc = template.get("description", "No description")
            emoji = template.get("emoji_usage", "unknown")
            hashtags = template.get("hashtag_count", "?")
            print(f"  {name}")
            print(f"    {desc}")
            print(f"    Emoji: {emoji}, Hashtags: {hashtags}")
            print()
        sys.exit(0)

    # Validate required args for posting
    if not args.folder:
        print("Error: --folder is required for posting", file=sys.stderr)
        sys.exit(1)

    folder_path = Path(args.folder).expanduser()
    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}", file=sys.stderr)
        sys.exit(1)

    # Determine caption: either direct --caption or from --template
    if args.caption and args.template:
        print("Error: Use --caption OR --template, not both", file=sys.stderr)
        sys.exit(1)

    if not args.caption and not args.template:
        print("Error: Must provide either --caption or --template", file=sys.stderr)
        sys.exit(1)

    if args.template:
        # Render caption from template
        try:
            caption = render_template(
                template_name=args.template,
                title=args.title or "",
                topic=args.topic or "",
                cta=args.cta or ""
            )
            print(f"Using template '{args.template}':", file=sys.stderr)
            print(f"---\n{caption}\n---", file=sys.stderr)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        caption = args.caption

    result = post_carousel(folder_path, caption)

    # Output result as JSON
    print(json.dumps(result, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
