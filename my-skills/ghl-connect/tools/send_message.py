#!/usr/bin/env python3
"""
Send GHL Message
================
Send an email reply or new message through GHL.

Usage:
    python3 send_message.py --contact-id <id> --subject "Subject" --html "<p>Body</p>" [options]

Options:
    --contact-id ID       Required: Contact ID to send to
    --subject TEXT        Email subject line
    --html TEXT           HTML body (string or @filepath)
    --reply-to MSG_ID     Message ID to reply to (threads the conversation)
    --dry-run             Show what would be sent without sending

Security:
    - ALWAYS use --dry-run first to verify formatting
    - Session send limit: 10 messages (configurable)
    - Requires explicit confirmation before sending
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Import shared client
sys.path.insert(0, str(Path(__file__).parent))
from ghl_client import GHLClient


def load_html_content(html_arg: str) -> str:
    """
    Load HTML content from argument.

    If starts with @, treat as file path.
    Otherwise, use as literal string.

    Args:
        html_arg: HTML string or @filepath

    Returns:
        HTML content string
    """
    if html_arg.startswith("@"):
        filepath = Path(html_arg[1:]).expanduser()
        if not filepath.exists():
            print(f"Error: HTML file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        return filepath.read_text()
    return html_arg


def send_email(client: GHLClient, contact_id: str, subject: str, html_body: str,
               reply_to_message_id: str = None, conversation_id: str = None) -> dict:
    """
    Send an email via GHL.

    Args:
        client: GHLClient instance
        contact_id: Recipient contact ID
        subject: Email subject
        html_body: HTML body content
        reply_to_message_id: Optional message ID to reply to
        conversation_id: Optional conversation ID for threading

    Returns:
        API response dict
    """
    # Build the message payload
    payload = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
    }

    # Add threading if replying
    if reply_to_message_id:
        payload["replyMessageId"] = reply_to_message_id

    if conversation_id:
        payload["conversationId"] = conversation_id

    # In test mode, we can't actually redirect the recipient via API
    # The test mode flag is for user workflow - they should verify with --dry-run first
    # then manually confirm before real send

    # Send via API
    response = client.post("/conversations/messages", data=payload)

    # Increment send counter
    client.increment_send_count()

    return response


def preview_message(contact_id: str, subject: str, html_body: str,
                    reply_to_message_id: str = None) -> str:
    """
    Generate a preview of what would be sent.

    Args:
        contact_id: Recipient contact ID
        subject: Email subject
        html_body: HTML body content
        reply_to_message_id: Optional reply message ID

    Returns:
        Formatted preview string
    """
    # Truncate body for preview
    body_preview = html_body[:500]
    if len(html_body) > 500:
        body_preview += "\n... [truncated]"

    preview = []
    preview.append("=" * 60)
    preview.append("📤 EMAIL PREVIEW")
    preview.append("=" * 60)
    preview.append(f"To: Contact ID {contact_id}")
    preview.append(f"Subject: {subject}")
    if reply_to_message_id:
        preview.append(f"Reply-To: {reply_to_message_id}")
    preview.append("-" * 60)
    preview.append("Body:")
    preview.append(body_preview)
    preview.append("=" * 60)

    return "\n".join(preview)


def main():
    """Send an email message."""
    parser = argparse.ArgumentParser(description="Send GHL Email")
    parser.add_argument("--contact-id", required=True,
                        help="Contact ID to send to")
    parser.add_argument("--subject", required=True,
                        help="Email subject line")
    parser.add_argument("--html", required=True,
                        help="HTML body (string or @filepath)")
    parser.add_argument("--reply-to", default=None,
                        help="Message ID to reply to (for threading)")
    parser.add_argument("--conversation-id", default=None,
                        help="Conversation ID (for threading)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show preview without sending")
    args = parser.parse_args()

    # Load HTML content
    html_body = load_html_content(args.html)

    # Initialize client
    client = GHLClient()

    # Check send limit
    if not client.check_send_limit():
        print(f"Error: Session send limit reached ({client.max_sends} messages).", file=sys.stderr)
        print("Start a new session to continue sending.", file=sys.stderr)
        sys.exit(1)

    # Show preview
    print(preview_message(
        args.contact_id,
        args.subject,
        html_body,
        args.reply_to
    ))

    if args.dry_run:
        print("\n✋ DRY RUN - Message NOT sent.")
        print("Remove --dry-run to actually send.")
        return

    # Confirm before sending
    print("\n📬 Ready to send?")
    print("    Sends remaining this session:", client.max_sends - client.sends_this_session)

    try:
        confirm = input("    Type 'yes' to send: ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
    except EOFError:
        # Non-interactive mode - don't send without explicit yes
        print("Error: Cannot send in non-interactive mode without confirmation.", file=sys.stderr)
        print("Use this script interactively or build a wrapper that handles confirmation.", file=sys.stderr)
        sys.exit(1)

    # Send the message
    print("\nSending...")
    try:
        result = send_email(
            client,
            args.contact_id,
            args.subject,
            html_body,
            args.reply_to,
            args.conversation_id
        )

        print("✅ Message sent!")
        print(f"   Conversation ID: {result.get('conversationId', 'N/A')}")
        print(f"   Message ID: {result.get('messageId', 'N/A')}")

    except Exception as e:
        print(f"❌ Send failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
