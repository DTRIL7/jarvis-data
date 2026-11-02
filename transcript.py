"""Fetch YouTube transcripts for the Jarvis LAB (research only). Usage: python transcript.py ID [ID ...]"""
import sys, json, re
from youtube_transcript_api import YouTubeTranscriptApi

def vid(x):
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", x)
    return m.group(1) if m else x.strip()

api = YouTubeTranscriptApi()
for raw in sys.argv[1:]:
    v = vid(raw)
    try:
        t = api.fetch(v, languages=["en", "en-US", "en-GB"])
        text = "\n".join(s.text for s in t)
        open(f"transcripts/{v}.txt", "w").write(text)
        print(f"ok {v}: {len(text)} chars")
    except Exception as e:
        open(f"transcripts/{v}.error.txt", "w").write(f"{type(e).__name__}: {e}")
        print(f"FAILED {v}: {type(e).__name__}: {str(e)[:300]}")
