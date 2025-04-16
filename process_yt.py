import pandas as pd
import numpy as np
import re
import httpx
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_transcript(question):
    file_path = os.path.join(os.path.dirname(__file__), "transcript.xlsx")
    df = pd.read_excel(file_path)
    match = re.search(
        r'between (\d+\.\d+) and (\d+\.\d+) seconds?', question, re.IGNORECASE)
    start_time = float(match.group(1))
    end_time = float(match.group(2))

    transcript = ""
    for index, row in df.iterrows():
        if row['timestamp'] >= start_time-1 and row['timestamp'] <= end_time+1:
            transcript += str(row['text'])+" "
    # print(transcript)
    return transcript

def correct_transcript(transcript):
    BASE_URL = "https://aiproxy.sanand.workers.dev/openai/v1"
    API_KEY = os.getenv("AIPROXY_TOKEN")
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "correct this transcript: "+transcript+" return only the answer and nothing else , not extra text"}]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    response = httpx.post(BASE_URL + "/chat/completions",
                          json=data, headers=headers, timeout=120)

    return response.json().get("choices", [])[0].get("message", {}).get("content")

# question = "What is the text of the transcript of this Mystery Story Audiobook between 404.9 and 478.3 seconds?"
# print(correct_transcript(get_transcript(question)))
