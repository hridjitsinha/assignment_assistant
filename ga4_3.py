from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from lxml import html

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WIKIPEDIA_BASE_URL = "https://en.wikipedia.org/wiki/"

@app.get("/api/outline")
async def get_country_outline(country: str = Query(..., title="Country Name", description="Name of the country")):
    """Fetches the Wikipedia page of the country, extracts headings, and returns a Markdown outline."""
    
    url = WIKIPEDIA_BASE_URL + country.replace(" ", "_")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"error": "Could not fetch Wikipedia page"}

            html_content = await response.text()

    tree = html.fromstring(html_content)
    
    # Extract headings using XPath
    headings = tree.xpath("//h1 | //h2 | //h3 | //h4 | //h5 | //h6")

    if not headings:
        return {"error": "No headings found on the Wikipedia page"}

    markdown_outline = "## Contents\n\n"
    for heading in headings:
        level = int(heading.tag[1])  # Extract level from H1, H2, ..., H6
        markdown_outline += f"{'#' * level} {heading.text_content().strip()}\n\n"
        
    print({"country": country, "outline": markdown_outline})
    return {"country": country, "outline": markdown_outline}
