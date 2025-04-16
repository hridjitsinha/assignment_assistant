from ga1 import GA1_2, GA1_3, GA1_4, GA1_5, GA1_6, GA1_7, GA1_8, GA1_9, GA1_10, GA1_11, GA1_12, GA1_14, GA1_15, GA1_16, GA1_17, GA1_18
from ga2 import GA2_2, GA2_4, GA2_5, GA2_5_file, GA2_9_old
from ga2_9 import read_student_data, get_students
from ga3 import GA3_1, GA3_2, GA3_3, GA3_4, GA3_5, GA3_6
from ga4 import GA4_1, GA4_2, GA4_4, GA4_5, GA4_6, GA4_7,GA4_9_without_pdfplumber, GA4_10
from ga5 import GA5_1, GA5_2, GA5_3, GA5_3_file, GA5_4, GA5_4_file, GA5_5, GA5_6, GA5_7, GA5_8, GA5_10, GA5_9
import asyncio
import aiofiles
import subprocess
import os
from pdf_processing import upload_to_vercel

async def fetch_answer(task_id, question, file_path):
    # if task_id == 'GA1.1': extract from excel
    if task_id == 'GA1.2':
        answer = GA1_2(question)
    if task_id == 'GA1.3':
        answer = await GA1_3(file_path)
    if task_id == 'GA1.4':
        answer = GA1_4(question)
    if task_id == 'GA1.5':
        answer = GA1_5(question)
    if task_id == 'GA1.6':
        answer = GA1_6(question, file_path)
    if task_id == 'GA1.7':
        answer = GA1_7(question)
    if task_id == 'GA1.8':
        answer = GA1_8(question, file_path)
    if task_id == 'GA1.9':
        answer = GA1_9(question)
    if task_id == 'GA1.10':
        answer = await GA1_10(file_path)
    if task_id == 'GA1.11':
        answer = GA1_11(question, file_path)
    if task_id == 'GA1.12':
        answer = await GA1_12(question, file_path)
    # if task_id == 'GA1.13': extract from excel
    if task_id == 'GA1.14':
        answer = await GA1_14(question, file_path)
    if task_id == 'GA1.15':
        answer = await GA1_15(question, file_path)
    if task_id == 'GA1.16':
        answer = await GA1_16(file_path)
    if task_id == 'GA1.17':
        answer = await GA1_17(question, file_path)
    if task_id == 'GA1.18':
        answer = GA1_18(question)
    # if task_id == 'GA2.1': extract from excel
    if task_id == 'GA2.2':
        answer = await GA2_2(file_path)
    # if task_id == 'GA2.3': extract from excel
    if task_id == 'GA2.4':
        answer = await GA2_4(question)
    if task_id == 'GA2.5':
        if file_path == "":
            answer = await GA2_5(question, "")
        else:
            answer = await GA2_5_file(question, file_path)
    # if task_id == 'GA2.6': extract from excel
    # if task_id == 'GA2.7': extract from excel
    # if task_id == 'GA2.8': extract from excel
    if task_id == 'GA2.9':
        port = 10000
        subprocess.Popen(["uvicorn", "ga2_9:app", "--host",
                         "0.0.0.0", "--port", str(port)])
        # GA2_9_old(file_path,port)
        # process.terminate()
        answer = f"http://127.0.0.1:{port}/api"
    # if task_id == 'GA2.10': extract from excel
    if task_id == 'GA3.1':
        answer = GA3_1(question)
    if task_id == 'GA3.2':
        answer = GA3_2(question)
    if task_id == 'GA3.3':
        answer = GA3_3(question)
    if task_id == 'GA3.4':
        answer = await GA3_4(question, file_path)
    if task_id == 'GA3.5':
        answer = GA3_5(question)
    if task_id == 'GA3.6':
        answer = GA3_6(question)
    # if task_id == 'GA3.7': extract from excel
    # if task_id == 'GA3.8': extract from excel
    # if task_id == 'GA3.9': extract from excel
    if task_id == 'GA4.1':
        answer = GA4_1(question)
    if task_id == 'GA4.2':
        answer = GA4_2(question)
    # if task_id == 'GA4.3': extract from excel
    if task_id == 'GA4.4':
        answer = GA4_4(question)
    if task_id == 'GA4.5':
        answer = GA4_5(question)
    if task_id == 'GA4.6':
        answer = GA4_6(question)
    if task_id == 'GA4.7':
        answer = GA4_7(question)
    # if task_id == 'GA4.8': extract from excel
    if task_id == 'GA4.9':
        if file_path!="":
            answer = await upload_to_vercel(question, file_path)
        else:
            answer = await GA4_9_without_pdfplumber(question)
    if task_id == 'GA4.10':
        answer = await GA4_10(question, file_path)
    if task_id == 'GA5.1':
        answer = await GA5_1(question, file_path)
    if task_id == 'GA5.2':
        answer = await GA5_2(question, file_path)
    if task_id == 'GA5.3':
        if file_path:
            answer = await GA5_3(question, file_path)
        else:
            file_path = os.path.join(os.path.dirname(
                __file__), "s-anand.net-May-2024.gz")
            async with aiofiles.open(file_path, "rb") as file:
                content = await file.read()
            answer = await GA5_3_file(question, content)
    if task_id == 'GA5.4':
        if file_path:
            answer = await GA5_4(question, file_path)
        else:
            file_path = os.path.join(os.path.dirname(
                __file__), "s-anand.net-May-2024.gz")
            async with aiofiles.open(file_path, "rb") as file:
                content = await file.read()
            answer = await GA5_4_file(question, content)
    if task_id == 'GA5.5':
        answer = await GA5_5(question, file_path)
    if task_id == 'GA5.6':
        answer = await GA5_6(question, file_path)
    if task_id == 'GA5.7':
        answer = await GA5_7(question, file_path)
    if task_id == 'GA5.8':
        answer = GA5_8(question)
    if task_id == 'GA5.9': 
        answer = await GA5_9(question)
    if task_id == 'GA5.10':
        answer = await GA5_10(question, file_path)
    return answer
