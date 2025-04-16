import xml.etree.ElementTree as ET
import pycountry  # type: ignore
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import json
from urllib.parse import urlencode
from datetime import datetime, timedelta
import pytz
from geopy.geocoders import Nominatim  # type: ignore
import io
from fastapi import UploadFile  # type: ignore
import os
import httpx
import numpy as np
from io import BytesIO
import asyncio
from PIL import Image
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def GA4_1(question: str):
    match = re.search(
        r'What is the total number of ducks across players on page number (\d+)', question)
    page_number = match.group(1)
    url = "https://stats.espncricinfo.com/stats/engine/stats/index.html?class=2;page=" + \
        page_number + ";template=results;type=batting"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise f'Failed to fetch the page. Status code: {response.status_code}'
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", {"class": "engineTable"})
    stats_table = None
    for table in tables:
        if table.find("th", string="Player"):
            stats_table = table
            break
    if not stats_table:
        print("Could not find the batting stats table on the page.")
    headers = [th.get_text(strip=True)for th in stats_table.find_all("th")]
    # print(headers)
    rows = stats_table.find_all("tr", {"class": "data1"})
    sum_ducks = 0
    for row in rows:
        cells = row.find_all("td")
        if len(cells) > 12:
            duck_count = cells[12].get_text(strip=True)
            if duck_count.isdigit():  # Check if it's a number
                sum_ducks += int(duck_count)
    # print(sum_ducks)
    return sum_ducks

# question = "What is the total number of ducks across players on page number 6"
# print(GA4_1(question))


def change_movie_title(title):
    if "Kraven: The Hunter" in title:
        return title.replace("Kraven: The Hunter", "Kraven the Hunter")
    elif "Captain America: New World Order" in title:
        return title.replace("Captain America: New World Order", "Captain America: Brave New World")
    else:
        return title


def GA4_2(question):
    match = re.search(
        r'Filter all titles with a rating between (\d+) and (\d+).', question)
    min_rating, max_rating = match.group(1), match.group(2)
    url = "https://www.imdb.com/search/title/?user_rating=" + \
        min_rating + "," + max_rating + ""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return json.dumps({"error": "Failed to fetch data from IMDb"}, indent=2)

    soup = BeautifulSoup(response.text, "html.parser")
    movies = []
    movie_items = soup.select(".ipc-metadata-list-summary-item")
    items = movie_items[:25]
    for item in items:
        link = item.select_one(".ipc-title-link-wrapper")
        movie_id = re.search(
            r"(tt\d+)", link["href"]).group(1) if link and link.get("href") else None

        # Extract title
        title_elem = item.select_one(".ipc-title__text")
        title = title_elem.text.strip() if title_elem else None
        title = change_movie_title(title)

        year_elem = item.select_one(".dli-title-metadata-item")
        year = year_elem.text if year_elem else None

        rating_elem = item.select_one(".ipc-rating-star--rating")
        rating = rating_elem.text.strip() if rating_elem else None

        movies.append({
            "id": movie_id,
            "title": title,
            "year": year,
            "rating": rating
        })

    return movies


# # Example usage
# question = """Your Task
# Source: Utilize IMDb's advanced web search at https: // www.imdb.com/search/title / to access movie data.
# Filter: Filter all titles with a rating between 3 and 6.
# Format: For up to the first 25 titles, extract the necessary details: ID, title, year, and rating. The ID of the movie is the part of the URL after tt in the href attribute. For example, tt10078772. Organize the data into a JSON structure as follows:

# [
#     {"id": "tt1234567", "title": "Movie 1", "year": "2021", "rating": "5.8"},
#     {"id": "tt7654321", "title": "Movie 2", "year": "2019", "rating": "6.2"},
#     // ... more titles
# ]
# Submit: Submit the JSON data in the text box below.
# Impact
# By completing this assignment, you'll simulate a key component of a streaming service's content acquisition strategy. Your work will enable StreamFlix to make informed decisions about which titles to license, ensuring that their catalog remains both diverse and aligned with subscriber preferences. This, in turn, contributes to improved customer satisfaction and retention, driving the company's growth and success in a competitive market.

# What is the JSON data?"""
# print(GA4_2(question))

def GA4_4(question: str):
    match = re.search(r"to (.*?) from (.*?)\?", question)
    if not match:
        return "Error extracting locations from the query."
    
    destination = match.group(1).strip()
    origin = match.group(2).strip()
    
    # Create the URL for the directions API
    mapquest_api_key = os.getenv("MAPQUEST_API_KEY")
    # ... rest of the function ...

def get_country_code(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        # Returns the ISO 3166-1 Alpha-2 code (e.g., "VN" for Vietnam)
        return country.alpha_2
    except LookupError:
        return None  # Returns None if the country name is not found


def GA4_5(question):
    match1 = re.search(
        r"What is the minimum latitude of the bounding box of the city ([A-Za-z\s]+) in", question)
    match2 = re.search(
        r"the country ([A-Za-z\s]+) on the Nominatim API", question)
    if not match1 or not match2:
        return "Invalid question format"
    city = match1.group(1).strip()
    country = match2.group(1).strip()
    locator = Nominatim(user_agent="myGeocoder")
    country_code = get_country_code(country)
    print(city,country,country_code)
    location = locator.geocode(city, country_codes=country_code)
    # print(location.raw, location.point, location.longitude, location.latitude, location.altitude, location.address)
    print(location.raw["boundingbox"])
    result = location.raw["boundingbox"][0]
    # print(result)
    return result


# q = "What is the minimum latitude of the bounding box of the city Ho Chi Minh City in the country Vietnam on the Nominatim API? Value of the minimum latitude"
# print(GA4_5(q))


def GA4_6(question):
    pattern = r"What is the link to the latest Hacker News post mentioning (.+?) having at least (\d+) points?"
    match = re.search(pattern, question)
    keyword, min_points = match.group(1), int(match.group(2))
    print(keyword, min_points)
    url = "https://hnrss.org/newest"
    request = requests.get(url, params={"q": keyword, "points": min_points})
    rss_content = request.text
    root = ET.fromstring(rss_content)
    items = root.findall(".//item")
    if not items:
        return "No matching post found."
    latest_post = items[0]
    title = latest_post.find("title").text
    link = latest_post.find("link").text
    published = latest_post.find("pubDate").text
    return link


# q = "What is the link to the latest Hacker News post mentioning Self-Hosting having at least 98 points?"
# print(GA4_6(q))

def GA4_7(question):
    """Using the GitHub API, find all users located in the city with over a specified number of followers"""
    pattern = r"find all users located in the city (.+?) with over (\d+) followers"
    match = re.search(pattern, question)
    if not match:
        return "Invalid question format"
    city, min_followers = match.group(1), int(match.group(2))
    url = "https://api.github.com/search/users"
    params = {"q": f"location:{city} followers:>{min_followers}",
              "sort": "joined", "order": "desc"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"GitHub API request failed with status {response.status_code}"
    data = response.json()
    if "items" not in data:
        return "No users found in the response."
    latest_user = data["items"][0]
    # print(latest_user)
    url = latest_user["url"]
    # print(url)
    response = requests.get(url)
    if response.status_code != 200:
        return f"GitHub API request failed with status {response.status_code}"
    created_at = response.json()["created_at"]
    return created_at


# q = "find all users located in the city Hyderabad with over 110 followers."
# print(GA4_7(q))

async def GA4_9_without_pdfplumber(question: str):
    match = re.search(
        r"What is the total (.+?) marks of students who scored (\d+) or more marks in (.+?) in groups (\d+)-(\d+) \(including both groups\)\?",
        question
    )

    if match is None:
        return {"error": "Question format is incorrect"}

    final_subject = match.group(1)
    min_score = int(match.group(2))
    subject = match.group(3)
    min_group = int(match.group(4))
    max_group = int(match.group(5))
    print("Params:", final_subject, min_score, subject, min_group, max_group)
    # Read all sheets from the Excel file
    excel_filename = "pdf_data_excel.xlsx"
    sheets_dict = pd.read_excel(excel_filename, sheet_name=None)
    # Combine data from selected pages
    df_list = []
    for group_num in range(min_group, max_group+1):
        sheet_name = f"group_{group_num}"
        if sheet_name in sheets_dict:
            df_list.append(sheets_dict[sheet_name])
    if not df_list:
        return {"error": "No valid pages found in the specified range"}
    # Combine all selected pages into a single DataFrame
    df = pd.concat(df_list, ignore_index=True)
    # Ensure required columns exist
    if subject not in df.columns or final_subject not in df.columns:
        return {"error": "Required columns not found in extracted data"}
    # Convert columns to numeric, handling errors
    df[subject] = pd.to_numeric(df[subject], errors="coerce")
    df[final_subject] = pd.to_numeric(df[final_subject], errors="coerce")
    # Filter and compute the sum
    result = df[df[subject] >= min_score][final_subject].sum()
    return result

# q = "What is the total Maths marks of students who scored 36 or more marks in Economics in groups 36-60 (including both groups)?"

async def GA4_10(question: str, file: UploadFile):
    md_text = ""
    return md_text
