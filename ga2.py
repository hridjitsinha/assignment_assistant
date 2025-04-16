import csv
import uvicorn # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from fastapi import FastAPI, Query, HTTPException # type: ignore
import zipfile
import requests
from PIL import Image
import numpy as np
import colorsys
import os
import io
import base64
from fastapi import UploadFile # type: ignore
import subprocess
import asyncio
import hashlib
import re

# FastAPI app
app = FastAPI()

def extract_zip_file(source: str, extract_folder: str) -> str:
    """Extracts a ZIP file from a URL or local path."""

    zip_path = "temp.zip" if source.startswith("http") else source

    if source.startswith("http"):  # Download ZIP if source is a URL
        try:
            with requests.get(source, stream=True) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    f.write(r.content)
        except requests.RequestException as e:
            raise ValueError(f"Error downloading ZIP file: {e}")

    if os.path.isfile(extract_folder):  # Prevent extracting into a file
        raise ValueError(f"'{extract_folder}' is a file, not a directory.")

    os.makedirs(extract_folder, exist_ok=True)  # Ensure directory exists

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)
    except zipfile.BadZipFile:
        raise ValueError(
            f"Failed to extract ZIP file: {zip_path} is not a valid ZIP archive.")

    if source.startswith("http"):
        os.remove(zip_path)  # Cleanup downloaded ZIP

    return extract_folder

async def GA2_2(file, max_size=1500, target_width=800):
    temp_dir = "/tmp/" if os.getenv("VERCEL") else "compressed_images/"
    os.makedirs(temp_dir, exist_ok=True)

    temp_path = os.path.join(
        temp_dir, file.filename.rsplit(".", 1)[0] + ".png")

    # Open image
    img = Image.open(io.BytesIO(await file.read()))

    # Reduce color depth for PNG (if needed)
    if file.filename.lower().endswith(".png"):
        img = img.convert("P", palette=Image.ADAPTIVE)  # Reduce colors to 4
        img.save(temp_path, "PNG", optimize=True,bits=4)

    # Compression loop
    quality = 85
    while file.filename.lower().endswith in [".jpg", ".jpeg"]:
        img.save(temp_path, "JPEG", quality=quality, optimize=True)
        if os.path.getsize(temp_path) <= max_size or quality <= 10:
            break
        quality -= 5  # Reduce quality in steps

    # Encode to Base64
    with open(temp_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    print(f"Saved at: {temp_path}, Size: {os.path.getsize(temp_path)} bytes")
    return encoded  # Returning both path & Base64

def GA2_4(question: str):
   email = re.findall(
       r'Run this program on Google Colab, allowing all required access to your email ID: ([\w. % +-]+@[\w.-] +\.\w+)', question)[0]
   expiry_year = "2025"
   print(email, expiry_year)
   hash_value = hashlib.sha256(
       f"{email} {expiry_year}".encode()).hexdigest()[-5:]
   return hash_value

def download_image(url, filename="lenna.webp"):
    """Downloads an image from the given URL and returns its absolute path."""
    BASE_DIR = "/tmp" if os.getenv("VERCEL") else "."
    response = requests.get(url, stream=True)
    if response.ok:
        with open(filename, "wb") as file:
            file.write(response.content)
            if BASE_DIR == ".":
               return os.path.abspath(filename)
            return os.path.abspath(os.path.join(BASE_DIR, filename))
    raise Exception(
        f"Failed to download image, status code: {response.status_code}")

def count_light_pixels(image_path: str, threshold: float = 0.814):
    """Counts the number of pixels in an image with lightness above the threshold."""
    image = Image.open(image_path).convert("RGB")
    rgb = np.array(image) / 255.0
    lightness = np.apply_along_axis(lambda x: colorsys.rgb_to_hls(*x)[1], 2, rgb)
    light_pixels = np.sum(lightness > threshold)
    print(f'Number of pixels with lightness > {threshold}: {light_pixels}')
    return light_pixels

async def GA2_5(question: str, image_path: str):
    if image_path=="":
        image_path = download_image("https://exam.sanand.workers.dev/lenna.webp")
    threshold = re.search(
        r'Number of pixels with lightness > (\d+\.\d+)', question)[1]
    print(image_path, threshold)
    light_pixels = count_light_pixels(image_path, float(threshold))
    return int(light_pixels)

async def GA2_5_file(question: str, file: UploadFile):
    threshold = re.search(
        r'Number of pixels with lightness > (\d+\.\d+)', question)[1]
    threshold = float(threshold)
    image_path = io.BytesIO(await file.read())
    print(image_path, threshold)
    light_pixels = count_light_pixels(image_path, threshold)
    return int(light_pixels)

async def load_student_data(file: UploadFile):
    """Load student data from the uploaded CSV file."""
    students_data = []
    try:
        contents = await file.read()  # Read the uploaded file
        decoded_content = contents.decode("utf-8")  # Decode content to UTF-8
        csv_reader = csv.DictReader(io.StringIO(decoded_content))  # Parse CSV

        # Process CSV data and store it
        students_data = [
            {"studentId": int(row["studentId"]), "class": row["class"]}
            for row in csv_reader
        ]
    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")
    
    print(students_data)
    return students_data

async def load_and_set_data(file: UploadFile):
    """Asynchronously load and set the student data."""
    return await load_student_data(file)

def GA2_9_old(file_path: str, port: int):
    """Initializes FastAPI with student data loaded from an uploaded CSV file and runs the API in a background process using subprocess."""

    # Middleware for CORS support
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    # Store student data in memory
    students_data = []
    print(file_path)
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            students_data.append(
            {"studentId": int(row["studentId"]), "class": row["class"]})

    @app.get("/api")
    async def get_students(class_: list[str] = Query(default=None, alias="class")):
        """Fetch all students or filter by class(es)."""
        print(students_data)
        # if not students_data:
        #     raise HTTPException(status_code=400, detail="No data available.")

        print(class_)
        if class_:
            filtered_students = [
                s for s in students_data if s["class"] in class_]
            return JSONResponse(content={"students": filtered_students})
        return JSONResponse(content={"students": students_data})

    def run_api():
        """Function to run FastAPI without blocking execution."""
        uvicorn.run(app, host="0.0.0.0", port=port)

    # Run FastAPI in a background process using subprocess
    subprocess.Popen(["uvicorn", "ga2:app", "--host",
                     "0.0.0.0", "--port", str(port)])

    # Return the URL for the API endpoint
    return f"http://127.0.0.1:{port}/api"
