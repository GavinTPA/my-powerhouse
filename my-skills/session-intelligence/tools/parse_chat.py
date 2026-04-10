#!/usr/bin/env python3
"""
Session Intelligence — Chat Analysis Engine
=============================================
Parses Zoom chat logs, detects trainer prompts via burst patterns,
and maps participant responses to prompt windows.

Usage:
    python3 parse_chat.py --file <chat.txt> --hosts "Taki Moore,Toni Bache,Ed Dale"

Options:
    --file PATH        Path to Zoom chat file (.txt)
    --hosts NAMES      Comma-separated host/trainer names
    --burst-threshold  Min responses to detect a prompt (default: 5)
    --window-secs      Response window in seconds (default: 180)
    --json             Output as JSON

Output:
    Structured analysis with detected prompts, per-person response mapping,
    engagement stats, and prompt code assignments.

Zoom chat formats supported:
    HH:MM:SS    From  Sender Name : Message text
    HH:MM:SS    From  Sender Name  to  Everyone : Message text
    HH:MM:SS\\tSender Name:\\tMessage text
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict


# ── Chat Parsing ──────────────────────────────────────────────────

def parse_timestamp(ts: str) -> int:
    """Convert HH:MM:SS to total seconds."""
    parts = ts.split(":")
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])


def format_timestamp(seconds: int) -> str:
    """Convert total seconds back to HH:MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_chat(content: str) -> list:
    """
    Parse a Zoom chat log file.
    Returns list of messages: [{timestamp, timestamp_secs, sender, recipient, text}]
    """
    messages = []
    lines = content.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Format 1: "HH:MM:SS  From  Name : text" or "HH:MM:SS  From  Name  to  Recipient : text"
        match = re.match(
            r"(\d{2}:\d{2}:\d{2})\s+"
            r"From\s+(.+?)"
            r"(?:\s+to\s+(.+?))?"
            r"\s*:\s*(.+)",
            line
        )

        # Format 2: "HH:MM:SS\tName:\ttext"
        if not match:
            match2 = re.match(
                r"(\d{2}:\d{2}:\d{2})\t"
                r"(.+?):\t"
                r"(.+)",
                line
            )
            if match2:
                ts = match2.group(1)
                messages.append({
                    "timestamp": ts,
                    "timestamp_secs": parse_timestamp(ts),
                    "sender": match2.group(2).strip(),
                    "recipient": "Everyone",
                    "text": match2.group(3).strip()
                })
                continue

        if match:
            ts = match.group(1)
            messages.append({
                "timestamp": ts,
                "timestamp_secs": parse_timestamp(ts),
                "sender": match.group(2).strip(),
                "recipient": (match.group(3) or "Everyone").strip(),
                "text": match.group(4).strip()
            })
        else:
            # Continuation line — append to previous
            if messages:
                messages[-1]["text"] += " " + line

    return messages


# ── Host Detection ────────────────────────────────────────────────

def normalize_name(name: str) -> str:
    """Normalize name for matching (lowercase, stripped)."""
    return name.strip().lower()


def is_host(sender: str, host_names: list) -> bool:
    """Check if sender matches any host name (fuzzy: checks if any host name is contained in sender)."""
    sender_norm = normalize_name(sender)
    for host in host_names:
        host_norm = normalize_name(host)
        # Exact match or contained match (handles "Taki Moore's iPhone" etc.)
        if host_norm == sender_norm or host_norm in sender_norm or sender_norm in host_norm:
            return True
    return False


# ── Prompt Detection ──────────────────────────────────────────────

def is_noise_message(text: str) -> bool:
    """Check if a message is a reaction, emoji-only, or system noise — not a real prompt."""
    text_stripped = text.strip()
    # Zoom reactions: "Reacted to "..." with ❤️"
    if text_stripped.startswith("Reacted to"):
        return True
    # Reply-quote messages: "Replying to "..." <actual text>"
    # These are follow-ups, not fresh prompts — handled separately
    if text_stripped.startswith("Replying to"):
        return True
    # Emoji-only messages
    if len(text_stripped) <= 4 and not any(c.isalpha() for c in text_stripped):
        return True
    return False


def count_unique_responders(messages: list, start_idx: int, host_names: list,
                            window_start: int, window_end: int) -> tuple:
    """
    Count unique non-host responders in a time window.
    Returns (unique_count, total_responses).
    Unique responders is a stronger signal than total messages
    (one person posting 5 times isn't a burst — 5 people posting once is).
    """
    responders = set()
    total = 0
    for j in range(start_idx, len(messages)):
        later = messages[j]
        if later["timestamp_secs"] > window_end:
            break
        if not is_host(later["sender"], host_names):
            responders.add(later["sender"])
            total += 1
    return len(responders), total


def detect_prompts(messages: list, host_names: list,
                   burst_threshold: int = 5, window_secs: int = 180) -> list:
    """
    Detect prompt moments by finding host messages that trigger response bursts.

    Algorithm:
    1. Find each host message sent to Everyone (skip reactions, replies, noise)
    2. Count UNIQUE non-host responders within window_secs after the host message
    3. If unique responders >= burst_threshold, it's a prompt
    4. Deduplicate: if multiple host messages trigger overlapping bursts,
       keep only the one with the most unique responders

    Returns list of prompts:
    [{
        index: int,
        host_message: dict,
        response_count: int,
        unique_responders: int,
        window_start: int (secs),
        window_end: int (secs),
        code: str (auto-generated abbreviation)
    }]
    """
    candidates = []

    for i, msg in enumerate(messages):
        if not is_host(msg["sender"], host_names):
            continue
        if msg["recipient"] != "Everyone":
            continue
        # Skip reactions, reply-quotes, and emoji-only messages
        if is_noise_message(msg["text"]):
            continue

        window_start = msg["timestamp_secs"]
        window_end = window_start + window_secs

        unique_count, total_count = count_unique_responders(
            messages, i + 1, host_names, window_start, window_end
        )

        if unique_count >= burst_threshold:
            candidates.append({
                "host_message": msg,
                "unique_responders": unique_count,
                "response_count": total_count,
                "window_start": window_start,
                "window_end": window_end,
                "prompt_text": msg["text"]
            })

    # Deduplicate overlapping candidates: keep highest unique responders per 60s cluster
    prompts = deduplicate_prompts(candidates)

    # Assign codes and indices
    for i, p in enumerate(prompts, 1):
        p["index"] = i
        p["code"] = generate_prompt_code(p["prompt_text"], i)

    # Resolve overlapping windows
    prompts = resolve_windows(prompts)

    return prompts


def deduplicate_prompts(candidates: list, cluster_secs: int = 60) -> list:
    """
    When multiple host messages within cluster_secs seconds all trigger bursts,
    keep only the one with the most unique responders.
    This handles rapid-fire host messages that are all part of one prompt moment.
    """
    if not candidates:
        return []

    result = []
    cluster = [candidates[0]]

    for c in candidates[1:]:
        if c["window_start"] - cluster[0]["window_start"] <= cluster_secs:
            cluster.append(c)
        else:
            # Pick the best from this cluster
            best = max(cluster, key=lambda x: x["unique_responders"])
            result.append(best)
            cluster = [c]

    # Don't forget the last cluster
    best = max(cluster, key=lambda x: x["unique_responders"])
    result.append(best)

    return result


def resolve_windows(prompts: list) -> list:
    """
    Adjust prompt windows so they don't overlap.
    Each prompt's window ends when the next prompt's window starts.
    """
    for i in range(len(prompts) - 1):
        next_start = prompts[i + 1]["window_start"]
        if prompts[i]["window_end"] > next_start:
            prompts[i]["window_end"] = next_start
    return prompts


def generate_prompt_code(text: str, index: int) -> str:
    """
    Generate a short prompt code from the message text.
    Tries to extract a meaningful abbreviation; falls back to P1, P2, etc.
    """
    text_lower = text.lower()

    # Common coaching prompt patterns
    patterns = [
        (r"\bwin\b", "WIN"),
        (r"\blesson\b|\blearned\b|\blearning\b", "LES"),
        (r"\btweak\b", "TAW"),
        (r"\bresonat", "RES"),
        (r"\bclient\b.*\bhow many\b|\bhow many\b.*\bclient", "CLI"),
        (r"\brevenue\b|\bincome\b|\bhow much\b", "REV"),
        (r"\bfree\b.*\bpaid\b|\b[12]\b.*free.*paid|type 1.*type 2", "F/P"),
        (r"\brelieved\b|\bhappy\b|\bthrilled\b", "RHT"),
        (r"\bgap\b|\bconcern\b|\bworr|\bchalleng|\bstruggl", "GAP"),
        (r"\bwhat did\b.*\bjust\b|\bwhat happened\b|\bwhat.*notice", "REV2"),
        (r"\bbest\b.*\bthing\b|\btakeaway\b|\bbiggest\b.*\bthing", "BEST"),
        (r"\bgoal\b|\btarget\b|\bwant\b.*\bachiev", "GOAL"),
        (r"\bintroduc|\bname\b.*\bwhere\b|\btell us about", "INTRO"),
        (r"\baction\b|\bnext step\b|\bcommit\b", "ACT"),
    ]

    for pattern, code in patterns:
        if re.search(pattern, text_lower):
            return code

    return f"P{index}"


# ── Response Mapping ──────────────────────────────────────────────

def map_responses(messages: list, prompts: list, host_names: list) -> dict:
    """
    Map each non-host message to the nearest prompt window.

    Returns dict keyed by prompt code:
    {
        "WIN": [
            {"sender": "Name", "text": "...", "timestamp": "HH:MM:SS"},
            ...
        ],
        "OTHER": [messages not in any prompt window]
    }
    """
    prompt_responses = {p["code"]: [] for p in prompts}
    prompt_responses["OTHER"] = []

    for msg in messages:
        if is_host(msg["sender"], host_names):
            continue

        # Find which prompt window this message falls in
        assigned = False
        for prompt in prompts:
            if prompt["window_start"] <= msg["timestamp_secs"] <= prompt["window_end"]:
                prompt_responses[prompt["code"]].append({
                    "sender": msg["sender"],
                    "text": msg["text"],
                    "timestamp": msg["timestamp"]
                })
                assigned = True
                break

        if not assigned:
            prompt_responses["OTHER"].append({
                "sender": msg["sender"],
                "text": msg["text"],
                "timestamp": msg["timestamp"]
            })

    return prompt_responses


# ── Per-Person Index ──────────────────────────────────────────────

def build_person_index(messages: list, prompts: list, host_names: list) -> dict:
    """
    Build a per-person index of all their messages organized by prompt.

    Returns dict keyed by sender name:
    {
        "Sender Name": {
            "message_count": int,
            "prompts": {
                "WIN": ["response text", ...],
                "LES": ["response text", ...],
                "OTHER": ["message text", ...]
            }
        }
    }
    """
    people = defaultdict(lambda: {"message_count": 0, "prompts": defaultdict(list)})

    for msg in messages:
        if is_host(msg["sender"], host_names):
            continue

        sender = msg["sender"]
        people[sender]["message_count"] += 1

        # Find which prompt window
        assigned = False
        for prompt in prompts:
            if prompt["window_start"] <= msg["timestamp_secs"] <= prompt["window_end"]:
                people[sender]["prompts"][prompt["code"]].append(msg["text"])
                assigned = True
                break

        if not assigned:
            people[sender]["prompts"]["OTHER"].append(msg["text"])

    # Convert defaultdicts to regular dicts for JSON serialization
    result = {}
    for name, data in sorted(people.items()):
        result[name] = {
            "message_count": data["message_count"],
            "prompts": dict(data["prompts"])
        }

    return result


# ── Engagement Stats ──────────────────────────────────────────────

def get_engagement_stats(messages: list, host_names: list) -> dict:
    """Calculate engagement statistics excluding hosts."""
    sender_counts = defaultdict(int)
    for msg in messages:
        if not is_host(msg["sender"], host_names):
            sender_counts[msg["sender"]] += 1

    sorted_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "total_messages": sum(c for _, c in sorted_senders),
        "unique_participants": len(sorted_senders),
        "top_10": sorted_senders[:10],
        "all_participants": sorted_senders
    }


# ── Main Analysis ─────────────────────────────────────────────────

def analyze_chat(file_path: str, host_names: list,
                 burst_threshold: int = 5, window_secs: int = 180) -> dict:
    """
    Full chat analysis pipeline.

    Returns structured analysis dict ready for document generation.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    messages = parse_chat(content)

    if not messages:
        print("Error: No messages found in chat log.", file=sys.stderr)
        sys.exit(1)

    prompts = detect_prompts(messages, host_names, burst_threshold, window_secs)
    prompt_responses = map_responses(messages, prompts, host_names)
    person_index = build_person_index(messages, prompts, host_names)
    engagement = get_engagement_stats(messages, host_names)

    # Extract host messages (for Training Summary — trainer answers)
    host_messages = [m for m in messages if is_host(m["sender"], host_names)]

    # Extract questions from participants
    questions = [m for m in messages
                 if not is_host(m["sender"], host_names) and "?" in m["text"]]

    return {
        "file": str(path),
        "total_messages": len(messages),
        "prompts_detected": len(prompts),
        "prompts": [
            {
                "code": p["code"],
                "prompt_text": p["prompt_text"],
                "host": p["host_message"]["sender"],
                "timestamp": p["host_message"]["timestamp"],
                "window": f"{format_timestamp(p['window_start'])}–{format_timestamp(p['window_end'])}",
                "response_count": p["response_count"]
            }
            for p in prompts
        ],
        "person_index": person_index,
        "engagement": engagement,
        "host_messages": host_messages,
        "participant_questions": questions,
        "prompt_responses": {k: len(v) for k, v in prompt_responses.items()}
    }


def main():
    parser = argparse.ArgumentParser(
        description="Session Intelligence — Chat Analysis Engine"
    )
    parser.add_argument("--file", required=True,
                        help="Path to Zoom chat file (.txt)")
    parser.add_argument("--hosts", required=True,
                        help="Comma-separated host/trainer names")
    parser.add_argument("--burst-threshold", type=int, default=5,
                        help="Min responses to detect a prompt (default: 5)")
    parser.add_argument("--window-secs", type=int, default=180,
                        help="Response window in seconds (default: 180)")
    parser.add_argument("--json", action="store_true",
                        help="Output full analysis as JSON")
    args = parser.parse_args()

    host_names = [h.strip() for h in args.hosts.split(",")]

    result = analyze_chat(
        args.file, host_names,
        burst_threshold=args.burst_threshold,
        window_secs=args.window_secs
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable summary
        print(f"\n{'='*60}")
        print(f"SESSION INTELLIGENCE — CHAT ANALYSIS")
        print(f"{'='*60}")
        print(f"File: {result['file']}")
        print(f"Total messages: {result['total_messages']}")
        print(f"Participants: {result['engagement']['unique_participants']}")
        print(f"Prompts detected: {result['prompts_detected']}")
        print()

        if result["prompts"]:
            print("DETECTED PROMPTS:")
            print("-" * 40)
            for p in result["prompts"]:
                print(f"  [{p['code']}] {p['timestamp']} — {p['prompt_text'][:80]}")
                print(f"         Window: {p['window']} | Responses: {p['response_count']}")
            print()

        print(f"ENGAGEMENT (top 10):")
        print("-" * 40)
        for name, count in result["engagement"]["top_10"]:
            print(f"  {name}: {count} messages")
        print()

        print(f"PERSON INDEX ({len(result['person_index'])} participants):")
        print("-" * 40)
        for name, data in list(result["person_index"].items())[:5]:
            codes = ", ".join(data["prompts"].keys())
            print(f"  {name} ({data['message_count']} msgs): {codes}")
        if len(result["person_index"]) > 5:
            print(f"  ... and {len(result['person_index']) - 5} more")


if __name__ == "__main__":
    main()
