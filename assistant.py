from fastapi import FastAPI, File, Form, UploadFile
import shutil
import os
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key='eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDQzMTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.4_QfcYiQAB7DTHMtUMyNprvu3Xz6ui-upXP17FFgEUM')
@app.post("/api/")
async def answer_assignment(question: str = Form(...), file: UploadFile = None):
    if file:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Process file if needed
        os.remove(file_path)
    
    prompt_message = (
        '''You are a highly advanced AI assistant with unparalleled expertise in answering advance technology questions. 
        Your goal is to derive the absolutely correct answer using any available knowledge, logical reasoning, and precise calculations.
        Leave no room for doubt, ensuring your response is accurate, well-structured, and direct. If necessary, break down complex problems, 
        analyze data rigorously, and verify your conclusions. Provide concise yet complete explanations and avoid unnecessary verbosity.
        Accuracy is paramount; find the correct answer by any means necessary.'''
    )
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt_message},
                  {"role": "user", "content": question}]
    )
    
    return {"answer": response.choices[0].message['content']}