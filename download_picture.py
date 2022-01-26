import os
import requests
from pathlib import Path
from urllib.parse import urlparse

PATH_IMAGES = "images"


def fetch_spacex_last_launch() -> None:
    url_all = "https://api.spacexdata.com/v4/launches"
    response = requests.get(url_all)
    response.raise_for_status()
    launches = response.json()
    for launch in launches[::-1]:
        urls = launch["links"]["flickr"]["original"]
        if urls:
            break
    for index, url in enumerate(urls):
        filename = f"spaceX_flight{launch['flight_number']}_{index}.jpg"
        download_image(url, filename)


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


if __name__ == "__main__":
    #fetch_spacex_last_launch()
    url = "https://example.com/txt/hello%20world.txt?v=9#python"
    print(get_ext(url))
