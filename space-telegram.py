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


def download_image(url: str, full_filename: str, params: dict = {}) -> None:
    headers = {"User-Agent": "download_picture"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    with open(full_filename, "wb") as file:
        file.write(response.content)


def get_ext(url: str) -> str:
    path = urlparse(url).path
    return Path(path).suffix


def fetch_spacex_last_launch(path_images: str) -> None:
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
        full_filename = Path(path_images).joinpath(filename)
        download_image(url, full_filename)


def fetch_nasa_apod(api_key: str, path_images: str, limit: int = 30) -> None:
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
        filename = Path(path_images).joinpath(f"nasa_apod_{apod_date}{ext}")
        download_image(url, filename)


def fetch_nasa_epic(api_key: str, path_images: str) -> None:
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
        params = {
            "api_key": api_key,
        }
        url = f"{archive_url}/{date_path}/png/{image_name}"

        filename = Path(path_images).joinpath(f"nasa_epic_{index}.png")
        download_image(url, filename, params)


if __name__ == "__main__":
    load_dotenv()
    nasa_api_key = os.getenv("NASA_API_KEY")
    bot_token = os.getenv("SPACEPHOTOS_TG_BOT_TOKEN")
    channel_id = os.getenv("SPACEPHOTOS_TG_CHANNEL_ID")
    delay = int(os.getenv("SPACEPHOTOS_DELAY", DEFAULT_DELAY))

    bot = telegram.Bot(token=bot_token)

    while True:
        filenames = []
        if Path(PATH_IMAGES).is_dir():
            filenames = os.listdir(PATH_IMAGES)
        if not filenames:
            Path(PATH_IMAGES).mkdir(parents=True, exist_ok=True)
            try:
                fetch_nasa_apod(api_key=nasa_api_key, path_images=PATH_IMAGES, limit=30)
            except requests.exceptions.HTTPError as error:
                print(f'An http-error has occurred: \
                    {error.response.status_code} {error.response.reason}')
            except requests.exceptions.Timeout:
                print('Error: Timeout expired')

            try:
                fetch_nasa_epic(api_key=nasa_api_key, path_images=PATH_IMAGES)
            except requests.exceptions.HTTPError as error:
                print(f'An http-error has occurred: \
                    {error.response.status_code} {error.response.reason}')
            except requests.exceptions.Timeout:
                print('Error: Timeout expired')

            try:
                fetch_spacex_last_launch(path_images=PATH_IMAGES)
            except requests.exceptions.HTTPError as error:
                print(f'An http-error has occurred: \
                    {error.response.status_code} {error.response.reason}')
            except requests.exceptions.Timeout:
                print('Error: Timeout expired')

            continue

        filename = choice(filenames)
        filepath = Path(PATH_IMAGES).joinpath(filename)
        with open(filepath, "rb") as photo_file:
            bot.send_photo(chat_id=channel_id, photo=photo_file)
        Path(filepath).unlink()

        sleep(delay)
