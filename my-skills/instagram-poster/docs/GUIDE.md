# Post Carousels and Reels Directly to Instagram

**macOS only.** Not supported on Windows.

## Getting Started

Run **"set up instagram poster"** to connect your Instagram account. The setup takes about 10 minutes and walks you through everything.

### Prerequisites

- Instagram Business or Creator account (not Personal)
- Facebook Page linked to your Instagram account

## How It Works

After generating carousel images, say **"post this carousel to Instagram"** and the skill handles:
- Uploading images to temporary staging (Vercel Blob)
- Creating the carousel container via Meta's API
- Publishing with your caption
- Cleaning up staged images

## Posting a Carousel

1. Create your carousel with the instagram-carousel agent
2. Generate images (say "generate images")
3. Say **"post this carousel to Instagram"**
4. Confirm the caption and image count
5. The skill publishes and returns the post URL

## Posting a Reel

1. Have your video file ready (MP4, 9:16 aspect ratio)
2. Say **"post this reel to Instagram"**
3. Provide the video path and caption

## Token Maintenance

Your authorization lasts 60 days. If you use the posting skill regularly, it auto-refreshes. If you see a "Token expired" error after a long break, say **"set up instagram poster"** to re-authorize.
