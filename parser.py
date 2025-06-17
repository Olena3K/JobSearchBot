import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode


def search_workua_jobs(query, max_results=7):
    search_url = f"https://www.work.ua/jobs-{query.replace(' ', '+')}/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return ["⚠️ Could not connect to Work.ua."]

    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.select("div.card.card-hover.card-visited.job-link")

    results = []
    for job in job_cards[:max_results]:
        title_tag = job.select_one("h2 > a")
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = "https://www.work.ua" + title_tag.get("href")
            results.append(f"🔗 {title}\n{link}")

    return results if results else ["😔 No jobs found. Try a different keyword."]
