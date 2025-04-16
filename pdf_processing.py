from fastapi import FastAPI, UploadFile, Form
import httpx

app = FastAPI()


async def send_file_to_vercel(question: str, file: UploadFile, vercel_url: str):
    """Sends an uploaded file to the deployed Vercel FastAPI endpoint."""
    url = f"{vercel_url}/process-pdf"
    files = {"file": (file.filename, file.file, file.content_type)}
    data = {"question": question}  # ✅ Ensure question is sent in form data

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.post(url, files=files, data=data, timeout=60)

    try:
        return response.json()["total_marks"]
    except Exception:
        return {"error": "Invalid response from server", "status_code": response.status_code}


@app.post("/upload-to-vercel")
async def upload_to_vercel(
    question: str = Form(...),  # ✅ Explicitly mark as Form data
    file: UploadFile = Form(...)
):
    return await send_file_to_vercel(question, file, "https://tds-ga4-9-telvinvargheses-projects.vercel.app")
