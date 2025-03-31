from fastapi import FastAPI, File, Form, UploadFile
import shutil
import os
import openai
import zipfile
import json
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Correct OpenAI Client Initialization
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_file_content(file_path):
    """Extract content from different file types."""
    content = ""

    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        content = df.to_string()
    elif file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.dumps(json.load(f), indent=2)
    elif file_path.endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            extracted_folder = "temp_extracted"
            zip_ref.extractall(extracted_folder)
            for extracted_file in zip_ref.namelist():
                extracted_path = os.path.join(extracted_folder, extracted_file)
                content += extract_file_content(extracted_path) + "\n\n"
            shutil.rmtree(extracted_folder)
    return content

@app.post("/api/")
async def answer_assignment(question: str = Form(...), file: UploadFile = None):
    file_content = ""

    if file:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_content = extract_file_content(file_path)
        os.remove(file_path)

    prompt_message = (
        "You are a highly advanced AI assistant with unparalleled expertise in answering advanced technology questions. "
        "Your goal is to derive the absolutely correct answer using any available knowledge, logical reasoning, and precise calculations. "
        "Leave no room for doubt, ensuring your response is accurate, well-structured, and direct. "
        "If necessary, break down complex problems, analyze data rigorously, and verify your conclusions. "
        "Accuracy is paramount; find the correct answer by any means necessary.\n\n"
        f"Here is some relevant file content that might help:\n\n{file_content}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt_message},
                  {"role": "user", "content": question}]
    )

    return {"answer": response.choices[0].message.content}

# Enable local debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
