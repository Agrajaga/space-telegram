import os
from random import choice
from time import sleep
from dotenv import load_dotenv
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
import telegram


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


def fetch_nasa_epic(api_key: str) -> None:
    url_api = "https://api.nasa.gov/EPIC/api/natural/images"
    url_archive = "https://api.nasa.gov/EPIC/archive/natural"
    params = {
        "api_key" : api_key,
    }

    response = requests.get(url_api, params=params)
    response.raise_for_status()
    descriptions = response.json()
    for index, description in enumerate(descriptions):
        name_image = description["image"]
        date_image = description["date"]

        date_formatted = date_image.split()[0].replace("-", "/")
        url = f"{url_archive}/{date_formatted}/png/{name_image}.png?api_key={api_key}"
        
        filename = f"nasa_epic_{index}.png"
        download_image(url, filename)



if __name__ == "__main__":
    load_dotenv()
    api_key_nasa = os.getenv("API_KEY_NASA")
    token_telegram = os.getenv("SPACEPHOTOSBOT_TOKEN")
    channel_id = os.getenv("SPACEPHOTOS_CHANNEL_ID")
    delay = int(os.getenv("SPACE_TELEGRAM_DELAY"))

    bot = telegram.Bot(token=token_telegram)

    while True:
        images = []
        if Path(PATH_IMAGES).is_dir():
            images = os.listdir(PATH_IMAGES)
        if not images: 
            fetch_nasa_apod(api_key=api_key_nasa, limit=30)
            fetch_nasa_epic(api_key=api_key_nasa)
            fetch_spacex_last_launch()
            continue

        image = choice(images)
        filename = Path(PATH_IMAGES).joinpath(image)
        bot.send_photo(chat_id=channel_id, photo=open(filename, "rb"))
        Path(filename).unlink()

        sleep(delay)
