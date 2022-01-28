import os
from pathlib import Path
from random import choice
from time import sleep
from urllib.parse import urlparse

import requests
import telegram
from dotenv import load_dotenv

PATH_IMAGES = "images"
DEFAULT_DELAY = 86400


def make_images_folder(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def download_image(url: str, filename: str) -> None:
    headers = {"User-Agent": "download_picture"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(f"{PATH_IMAGES}/{filename}", "wb") as file:
        file.write(response.content)


def get_ext(url: str) -> str:
    path = urlparse(url).path
    return Path(path).suffix


def fetch_spacex_last_launch() -> None:
    all_launches_url = "https://api.spacexdata.com/v4/launches"
    response = requests.get(all_launches_url)
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
    apod_url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": api_key,
        "count": limit,
    }
    response = requests.get(apod_url, params=params)
    response.raise_for_status()
    descriptions = response.json()
    for description in descriptions:
        if description["media_type"] != "image":
            continue
        url = description["url"]
        apod_date = description["date"]
        ext = get_ext(url)
        filename = f"nasa_apod_{apod_date}{ext}"
        download_image(url, filename)


def fetch_nasa_epic(api_key: str) -> None:
    api_url = "https://api.nasa.gov/EPIC/api/natural/images"
    archive_url = "https://api.nasa.gov/EPIC/archive/natural"
    params = {
        "api_key": api_key,
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()
    descriptions = response.json()
    for index, description in enumerate(descriptions):
        image_name = f"{description['image']}.png"
        image_date = description["date"]

        date_path = image_date.split()[0].replace("-", "/")
        url = f"{archive_url}/{date_path}/png/{image_name}?api_key={api_key}"

        filename = f"nasa_epic_{index}.png"
        download_image(url, filename)


if __name__ == "__main__":
    load_dotenv()
    nasa_api_key = os.getenv("NASA_API_KEY")
    telegram_token = os.getenv("SPACEPHOTOS_TG_BOT_TOKEN")
    channel_id = os.getenv("SPACEPHOTOS_TG_CHANNEL_ID")
    delay = int(os.getenv("SPACEPHOTOS_DELAY", DEFAULT_DELAY))

    bot = telegram.Bot(token=telegram_token)

    while True:
        images = []
        if Path(PATH_IMAGES).is_dir():
            images = os.listdir(PATH_IMAGES)
        if not images:
            make_images_folder(PATH_IMAGES)
            try:
                fetch_nasa_apod(api_key=nasa_api_key, limit=30)
            except requests.exceptions.HTTPError as error:
                print(f'An http-error has occurred: \
                    {error.response.status_code} {error.response.reason}')
            except requests.exceptions.Timeout:
                print('Error: Timeout expired')

            try:
                fetch_nasa_epic(api_key=nasa_api_key)
            except requests.exceptions.HTTPError as error:
                print(f'An http-error has occurred: \
                    {error.response.status_code} {error.response.reason}')
            except requests.exceptions.Timeout:
                print('Error: Timeout expired')

            try:
                fetch_spacex_last_launch()
            except requests.exceptions.HTTPError as error:
                print(f'An http-error has occurred: \
                    {error.response.status_code} {error.response.reason}')
            except requests.exceptions.Timeout:
                print('Error: Timeout expired')

            continue

        image = choice(images)
        filename = Path(PATH_IMAGES).joinpath(image)
        bot.send_photo(chat_id=channel_id, photo=open(filename, "rb"))
        Path(filename).unlink()

        sleep(delay)
