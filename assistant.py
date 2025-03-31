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

# Correct OpenAI API Key Setup
openai.api_key = os.getenv("OPENAI_API_KEY")

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

def extract_file_content(file_path):
    """Extract content from different file types."""
    content = ""

    try:
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
            extracted_folder = os.path.join(TEMP_DIR, "extracted")
            os.makedirs(extracted_folder, exist_ok=True)
            
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extracted_folder)
                for extracted_file in zip_ref.namelist():
                    extracted_path = os.path.join(extracted_folder, extracted_file)
                    content += extract_file_content(extracted_path) + "\n\n"
                    
            # Clean up extracted files
            shutil.rmtree(extracted_folder, ignore_errors=True)

    except Exception as e:
        content = f"Error processing file: {str(e)}"

    return content

@app.post("/api/")
async def answer_assignment(question: str = Form(...), file: UploadFile = None):
    file_content = ""

    if file:
        file_path = os.path.join(TEMP_DIR, f"temp_{file.filename}")
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            file_content = extract_file_content(file_path)
        finally:
            os.remove(file_path)  # Cleanup after processing

    prompt_message = (
        "You are a highly advanced AI assistant with unparalleled expertise in answering advanced technology questions. "
        "Your goal is to derive the absolutely correct answer using any available knowledge, logical reasoning, and precise calculations. "
        "Leave no room for doubt, ensuring your response is accurate, well-structured, and direct. "
        "If necessary, break down complex problems, analyze data rigorously, and verify your conclusions. "
        "Accuracy is paramount; find the correct answer by any means necessary.\n\n"
        f"Here is some relevant file content that might help:\n\n{file_content}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt_message},
                  {"role": "user", "content": question}]
    )

    return {"answer": response["choices"][0]["message"]["content"]}

# Enable local debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
