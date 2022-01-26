import os
from dotenv import load_dotenv
import requests
from pathlib import Path
from urllib.parse import urlparse


PATH_IMAGES = "images"


def download_image(url: str, filename: str) -> None:
    headers = {"User-Agent" : "download_picture"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    Path(PATH_IMAGES).mkdir(parents=True, exist_ok=True)
    with open(f"{PATH_IMAGES}/{filename}", "wb") as file:
        file.write(response.content)


def get_ext(url: str) -> str:
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext


def fetch_spacex_last_launch() -> None:
    url_all_launches = "https://api.spacexdata.com/v4/launches"
    response = requests.get(url_all_launches)
    response.raise_for_status()
    launches = response.json()
    for launch in launches[::-1]:
        urls = launch["links"]["flickr"]["original"]
        if urls:
            break
    for index, url in enumerate(urls):
        filename = f"spaceX_flight{launch['flight_number']}_{index}.jpg"
        download_image(url, filename)


def fetch_nasa_apod(api_key: str, limit: int = 30) -> None:
    url_apod = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key" : api_key,
        "count" : limit, 
    }

    response = requests.get(url_apod, params=params)
    response.raise_for_status()
    descriptions = response.json()
    for description in descriptions:
        if description["media_type"] != "image":
            continue
        url = description["url"]
        date_apod = description["date"]
        ext = get_ext(url)
        filename = f"nasa_apod_{date_apod}{ext}"
        download_image(url, filename)


if __name__ == "__main__":
    load_dotenv()
    api_key_nasa = os.getenv("API_KEY_NASA")

    fetch_nasa_apod(api_key=api_key_nasa, limit=30)
    #fetch_spacex_last_launch()
