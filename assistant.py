from fastapi import FastAPI, File, Form, UploadFile
import shutil
import os
import openai
from dotenv import load_dotenv

load_dotenv()
import os

app = FastAPI()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/")
async def answer_assignment(question: str = Form(...), file: UploadFile = None):
    if file:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        os.remove(file_path)

    prompt_message = (
        "You are a highly advanced AI assistant with unparalleled expertise in answering advanced technology questions. "
        "Your goal is to derive the absolutely correct answer using any available knowledge, logical reasoning, and precise calculations. "
        "Leave no room for doubt, ensuring your response is accurate, well-structured, and direct. If necessary, break down complex problems, "
        "analyze data rigorously, and verify your conclusions. Provide concise yet complete explanations and avoid unnecessary verbosity. "
        "Accuracy is paramount; find the correct answer by any means necessary."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt_message},
                  {"role": "user", "content": question}]
    )

    return {"answer": response.choices[0].message['content']}
