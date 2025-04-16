import jellyfish
import pandas as pd
import numpy as np
from datetime import datetime
import re
import gzip
from collections import defaultdict
from fuzzywuzzy import process  # type: ignore
import pycountry  # type: ignore
import json
import os
from PIL import Image, ImageDraw
import base64
from io import BytesIO
from fastapi import UploadFile  # type: ignore
import io
from process_yt import get_transcript, correct_transcript


def get_country_code(country_name: str) -> str:
    """Retrieve the standardized country code from various country name variations."""
    normalized_name = re.sub(r'[^A-Za-z]', '', country_name).upper()
    for country in pycountry.countries:
        names = {country.name, country.alpha_2, country.alpha_3}
        if hasattr(country, 'official_name'):
            names.add(country.official_name)
        if hasattr(country, 'common_name'):
            names.add(country.common_name)
        if normalized_name in {re.sub(r'[^A-Za-z]', '', name).upper() for name in names}:
            return country.alpha_2
    return "Unknown"  # Default value if not found


def parse_date(date):
    for fmt in ("%m-%d-%Y", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(date), fmt).date()
        except ValueError:
            continue
    return None


# Standardized country names mapping
COUNTRY_MAPPING = {
    "USA": "US", "U.S.A": "US", "United States": "US",
    "India": "IN", "IND": "IN", "Bharat": "IN",
    "UK": "GB", "U.K": "GB", "United Kingdom": "GB", "Britain": "GB",
    "France": "FR", "Fra": "FR", "FRA": "FR",
    "Brazil": "BR", "BRA": "BR", "BRAZIL": "BR", "BRASIL": "BR",
    "UAE": "AE", "U.A.E": "AE", "United Arab Emirates": "AE",
}


async def GA5_1(question, file:UploadFile):
    file_content = await file.read()
    file_path = BytesIO(file_content)
    match = re.search(
        r'What is the total margin for transactions before ([A-Za-z]{3} [A-Za-z]{3} \d{2} \d{4} \d{2}:\d{2}:\d{2} GMT[+\-]\d{4}) \(India Standard Time\) for ([A-Za-z]+) sold in ([A-Za-z]+)', question, re.IGNORECASE)
    filter_date = datetime.strptime(match.group(
        1), "%a %b %d %Y %H:%M:%S GMT%z").replace(tzinfo=None).date() if match else None
    target_product = match.group(2) if match else None
    target_country = get_country_code(match.group(3)) if match else None
    print(filter_date, target_product, target_country)

    # Load Excel file
    df = pd.read_excel(file_path)
    df['Customer Name'] = df['Customer Name'].str.strip()
    df['Country'] = df['Country'].str.strip().apply(get_country_code)
    # df["Country"] = df["Country"].str.strip().replace(COUNTRY_MAPPING)

    df['Date'] = df['Date'].apply(parse_date)
    # df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

    df["Product"] = df["Product/Code"].str.split('/').str[0]

    # Clean and convert Sales and Cost
    df['Sales'] = df['Sales'].astype(str).str.replace(
        "USD", "").str.strip().astype(float)
    df['Cost'] = df['Cost'].astype(str).str.replace(
        "USD", "").str.strip().replace("", np.nan).astype(float)
    df['Cost'].fillna(df['Sales'] * 0.5, inplace=True)
    df['TransactionID'] = df['TransactionID'].astype(str).str.strip()

    # Filter the data
    filtered_df = df[(df["Date"] <= filter_date) &
                     (df["Product"] == target_product) &
                     (df["Country"] == target_country)]

    # Calculate total sales, total cost, and total margin
    total_sales = filtered_df["Sales"].sum()
    total_cost = filtered_df["Cost"].sum()
    total_margin = (total_sales - total_cost) / \
        total_sales if total_sales > 0 else 0
    print(total_margin, total_cost, total_sales)
    return total_margin

async def GA5_2(question: str, file: UploadFile):
    """Extracts unique names and IDs from an uploaded text file."""
    file_content = await file.read()
    file_path = BytesIO(file_content)  # In-memory file-like object
    names, ids = set(), set()
    id_pattern = re.compile(r'[^A-Za-z0-9]+')  # Pattern to clean ID values
    # Read file line by line
    for line in file_path.read().decode("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        parts = line.rsplit('-', 1)  # Split only at the last '-'
        if len(parts) == 2:
            name = parts[0].strip()
            id_part = parts[1].strip()
            # Extract ID before 'Marks' if present, otherwise use entire id_part
            id_cleaned = id_pattern.sub("", id_part.split(
                'Marks')[0] if 'Marks' in id_part else id_part).strip()
            names.add(name)
            ids.add(id_cleaned)
    print(f"Unique Names: {len(names)}, Unique IDs: {len(ids)}")
    return len(ids)

async def GA5_3_file(question: str, file_content):
    """Count successful requests for a given request type and page section within a time range."""
    file_path = BytesIO(file_content)  # In-memory file-like object

    # Extract parameters from the question using regex
    match = re.search(
        r'What is the number of successful (\w+) requests for pages under (/[a-zA-Z0-9_/]+) from (\d+):00 until before (\d+):00 on (\w+)days?',
        question, re.IGNORECASE)

    if not match:
        return {"error": "Invalid question format"}

    request_type, target_section, start_hour, end_hour, target_weekday = match.groups()
    target_weekday = target_weekday.capitalize() + "day"

    status_min = 200
    status_max = 299

    print(f"Parsed Parameters: {start_hour} to {end_hour}, Type: {request_type}, Section: {target_section}, Day: {target_weekday}")

    successful_requests = 0

    try:
        with gzip.GzipFile(fileobj=file_path, mode="r") as gz_file:
            file_content = gz_file.read().decode("utf-8")
            file = file_content.splitlines()
            for line in file:
                parts = line.split()

                # Ensure the log line has the minimum required fields
                if len(parts) < 9:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

                time_part = parts[3].strip('[]')  # Extract timestamp
                request_method = parts[5].replace('"', '').upper()
                url = parts[6]
                status_code = int(parts[8])

                try:
                    log_time = datetime.strptime(
                        time_part, "%d/%b/%Y:%H:%M:%S")
                    log_time = log_time.astimezone()  # Ensure correct timezone
                except ValueError:
                    print(f"Skipping invalid date format: {time_part}")
                    continue

                request_weekday = log_time.strftime('%A')

                # Apply filters
                if (status_min <= status_code <= status_max and
                    request_method == request_type and
                    url.startswith(target_section) and
                    int(start_hour) <= log_time.hour < int(end_hour) and
                        request_weekday == target_weekday):
                    successful_requests += 1

    except Exception as e:
        return {"error": str(e)}

    return successful_requests

async def GA5_3(question: str, file: UploadFile):
    """Count successful requests for a given request type and page section within a time range."""

    file_content = await file.read()
    file_path = BytesIO(file_content)  # In-memory file-like object

    # Extract parameters from the question using regex
    match = re.search(
        r'What is the number of successful (\w+) requests for pages under (/[a-zA-Z0-9_/]+) from (\d+):00 until before (\d+):00 on (\w+)days?',
        question, re.IGNORECASE)

    if not match:
        return {"error": "Invalid question format"}

    request_type, target_section, start_hour, end_hour, target_weekday = match.groups()
    target_weekday = target_weekday.capitalize() + "day"

    status_min = 200
    status_max = 300

    print(f"Parsed Parameters: {start_hour} to {end_hour}, Type: {request_type}, Section: {target_section}, Day: {target_weekday}")

    successful_requests = 0

    try:
        with gzip.GzipFile(fileobj=file_path, mode="r") as gz_file:
            file_content = gz_file.read().decode("utf-8")
            file = file_content.splitlines()
            for line in file:
                parts = line.split()

                # Ensure the log line has the minimum required fields
                if len(parts) < 9:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

                time_part = parts[3].strip('[]')  # Extract timestamp
                request_method = parts[5].replace('"', '').upper()
                url = parts[6]
                status_code = int(parts[8])

                try:
                    log_time = datetime.strptime(
                        time_part, "%d/%b/%Y:%H:%M:%S")
                    log_time = log_time.astimezone()  # Ensure correct timezone
                except ValueError:
                    print(f"Skipping invalid date format: {time_part}")
                    continue

                request_weekday = log_time.strftime('%A')

                # Apply filters
                if (status_min <= status_code <= status_max and
                    request_method == request_type and
                    url.startswith(target_section) and
                    int(start_hour) <= log_time.hour < int(end_hour) and
                        request_weekday == target_weekday):
                    successful_requests += 1

    except Exception as e:
        return {"error": str(e)}

    return successful_requests

async def GA5_4_file(question: str, file_content):
    file_path = BytesIO(file_content)  # In-memory file-like object
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', question)
    target_date = datetime.strptime(date_match.group(
        1), "%Y-%m-%d").date() if date_match else None
    ip_bandwidth = defaultdict(int)
    log_pattern = re.search(
        r'Across all requests under ([a-zA-Z0-9]+)/ on', question)
    language_pattern = str("/"+log_pattern.group(1)+"/")
    print(language_pattern, target_date)
    with gzip.GzipFile(fileobj=file_path, mode="r") as gz_file:
        file_content = gz_file.read().decode("utf-8")
        file = file_content.splitlines()
        for line in file:
            parts = line.split()
            ip_address = parts[0]
            time_part = parts[3].strip('[]')
            request_method = parts[5].replace('"', '').upper()
            url = parts[6]
            status_code = int(parts[8])
            log_time = datetime.strptime(time_part, "%d/%b/%Y:%H:%M:%S")
            log_time = log_time.astimezone()  # Convert timezone if needed
            size = int(parts[9]) if parts[9].isdigit() else 0
            if (url.startswith(language_pattern) and log_time.date() == target_date):
                ip_bandwidth[ip_address] += int(size)
                # print(ip_address, time_part, url, size)
    top_ip = max(ip_bandwidth, key=ip_bandwidth.get, default=None)
    top_bandwidth = ip_bandwidth[top_ip] if top_ip else 0
    return top_bandwidth

async def GA5_4(question: str, file: UploadFile):
    file_content = await file.read()
    file_path = BytesIO(file_content)  # In-memory file-like object
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', question)
    target_date = datetime.strptime(date_match.group(
        1), "%Y-%m-%d").date() if date_match else None
    ip_bandwidth = defaultdict(int)
    log_pattern = re.search(
        r'Across all requests under ([a-zA-Z0-9]+)/ on', question)
    language_pattern = str("/"+log_pattern.group(1)+"/")
    print(language_pattern, target_date)
    with gzip.GzipFile(fileobj=file_path, mode="r") as gz_file:
        file_content = gz_file.read().decode("utf-8")
        file = file_content.splitlines()
        for line in file:
            parts = line.split()
            ip_address = parts[0]
            time_part = parts[3].strip('[]')
            request_method = parts[5].replace('"', '').upper()
            url = parts[6]
            status_code = int(parts[8])
            log_time = datetime.strptime(time_part, "%d/%b/%Y:%H:%M:%S")
            log_time = log_time.astimezone()  # Convert timezone if needed
            size = int(parts[9]) if parts[9].isdigit() else 0
            if (url.startswith(language_pattern) and log_time.date() == target_date):
                ip_bandwidth[ip_address] += int(size)
                # print(ip_address, time_part, url, size)
    top_ip = max(ip_bandwidth, key=ip_bandwidth.get, default=None)
    top_bandwidth = ip_bandwidth[top_ip] if top_ip else 0
    return top_bandwidth

def get_best_matches(target, choices, threshold=0.85):
    """Find all matches for target in choices with Jaro-Winkler similarity >= threshold."""
    target = target.lower()
    matches = [c for c in choices if jellyfish.jaro_winkler_similarity(
        target, c.lower()) >= threshold]
    return matches


async def GA5_5(question: str, file: UploadFile):
    file_content = await file.read()
    file_path = BytesIO(file_content)  # In-memory file-like object
    try:
        df = pd.read_json(file_path)  # Load JSON into a Pandas DataFrame
    except ValueError:
        raise ValueError(
            "Invalid JSON format. Ensure the file contains a valid JSON structure.")

    match = re.search(
        r'How many units of ([A-Za-z\s]+) were sold in ([A-Za-z\s]+) on transactions with at least (\d+) units\?',
        question
    )
    if not match:
        raise ValueError("Invalid question format")

    target_product, target_city, min_sales = match.group(1).strip(
    ).lower(), match.group(2).strip().lower(), int(match.group(3))

    if not {"product", "city", "sales"}.issubset(df.columns):
        raise KeyError(
            "Missing one or more required columns: 'product', 'city', 'sales'")

    df["product"] = df["product"].str.lower()
    df["city"] = df["city"].str.lower()

    unique_cities = df["city"].unique()
    similar_cities = get_best_matches(
        target_city, unique_cities, threshold=0.85)
    print(similar_cities)

    if not similar_cities:
        return 0  # No matching cities found

    # Filter data for matching cities
    filtered_df = df[
        (df["product"] == target_product) &
        (df["sales"] >= min_sales) &
        (df["city"].isin(similar_cities))
    ]

    return int(filtered_df["sales"].sum())

# Example usage
# file_path = "sales_data.csv"
# total_sales = GA5_5("How many units of Shirt were sold in Istanbul on transactions with at least 131 units?", file_path)
# print("Total sales:", total_sales)


def fix_sales_value(sales):
    """Try to convert sales value to a float or default to 0 if invalid."""
    if isinstance(sales, (int, float)):
        return float(sales)  # Already valid

    if isinstance(sales, str):
        sales = sales.strip()  # Remove spaces
        if re.match(r"^\d+(\.\d+)?$", sales):  # Check if it's a valid number
            return float(sales)

    return 0.0  # Default for invalid values

async def GA5_6(question: str, file: UploadFile):
    file_content = await file.read()
    lines = file_content.decode(
        "utf-8").splitlines()  # In-memory file-like object
    sales_data = []
    for idx, line in enumerate(lines, start=1):
        try:
            entry = json.loads(line.strip())  # Parse each JSON line
            if "sales" in entry:
                entry["sales"] = fix_sales_value(entry["sales"])  # Fix invalid sales
                sales_data.append(entry)
            else:
                print(f"Line {idx}: Missing 'sales' field, adding default 0.0")
                entry["sales"] = 0.0
                sales_data.append(entry)
        except json.JSONDecodeError:
            # print(
            #     f"Line {idx}: Corrupt JSON, skipping -> {line.strip()}")
            line = line.strip().replace("{", "").split(",")[:-1]
            line = json.dumps({k.strip('"'): int(v) if v.isdigit() else v.strip('"') for k, v in (item.split(":", 1) for item in line)})
            # print("Fixed",line)
            sales_data.append(json.loads(line.strip()))
    sales = int(sum(entry["sales"] for entry in sales_data))
    return sales

def count_keys_json(data, key_word):
    count = 0
    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_word:
                count += 1
            count += count_keys_json(value, key_word)
    elif isinstance(data, list):
        for item in data:
            count += count_keys_json(item, key_word)
    return count


async def GA5_7(question: str, file: UploadFile):
    file_content = await file.read()
    file_content = file_content.decode("utf-8")
    key = re.search(r'How many times does (\w+) appear as a key?', question).group(1)
    print(key)
    json_data = json.loads(file_content)
    count = count_keys_json(json_data, key)
    return count

# Example usage
# file_path = "q-extract-nested-json-keys.json"
# key_count = GA5_7("Download the data from q-extract-nested-json-keys.json. How many times does DX appear as a key?", file_path)
# print("Key count:", key_count)


def GA5_8(question):
    match1 = re.search(
        r"Write a DuckDB SQL query to find all posts IDs after (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z) with at least (\d+)", question)
    match2 = re.search(
        r" with (\d+) useful stars, sorted. The result should be a table with a single column called post_id, and the relevant post IDs should be sorted in ascending order.", question)
    datetime, comments,stars = match1.group(1), match1.group(2), match2.group(1)
    print(datetime, comments,stars)

    sql_query = f"""SELECT DISTINCT post_id FROM (SELECT timestamp, post_id, UNNEST (comments->'$[*].stars.useful') AS useful FROM social_media) AS temp
WHERE useful >= {stars}.0 AND timestamp > '{datetime}'
ORDER BY post_id ASC
"""
    return sql_query.replace("\n", " ")

# Example usage
# sql_query = GA5_8("Write a DuckDB SQL query to find all posts IDs after 2025-01-21T14: 36:47.099Z with at least 1 comment with 5 useful stars, sorted. The result should be a table with a single column called post_id, and the relevant post IDs should be sorted in ascending order.", file_path)
# print("Key count:", key_count)


async def GA5_9(question):
    transcript = get_transcript(question)
    try:
        correct_transcript(transcript)
        print(transcript)
    except Exception as e:
        print(transcript)
    return transcript


async def GA5_10(question: str, file: UploadFile):
    # Read file content into memory
    file_bytes = await file.read()
    scrambled_image = Image.open(io.BytesIO(file_bytes))

    # Image parameters
    grid_size = 5  # 5x5 grid
    piece_size = scrambled_image.width // grid_size  # Assuming a square image

    # Regex pattern to extract mapping data
    pattern = re.compile(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    mapping = [tuple(map(int, match)) for match in pattern.findall(question)]

    # Create a blank image for reconstruction
    reconstructed_image = Image.new(
        "RGB", (scrambled_image.width, scrambled_image.height))

    # Rearrange pieces based on the mapping
    for original_row, original_col, scrambled_row, scrambled_col in mapping:
        scrambled_x = scrambled_col * piece_size
        scrambled_y = scrambled_row * piece_size

        # Extract piece from scrambled image
        piece = scrambled_image.crop(
            (scrambled_x, scrambled_y, scrambled_x +
             piece_size, scrambled_y + piece_size)
        )

        # Place in correct position in the reconstructed image
        original_x = original_col * piece_size
        original_y = original_row * piece_size
        reconstructed_image.paste(piece, (original_x, original_y))

    # Convert to Base64
    img_io = io.BytesIO()
    reconstructed_image.save(img_io, format="PNG")
    image_b64 = base64.b64encode(img_io.getvalue()).decode()
    return image_b64
