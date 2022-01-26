import requests
from pathlib import Path


PATH_IMAGES = "images"


def download_image(url: str, filename: str) -> None:
    headers = {"User-Agent" : "download_picture"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    Path(PATH_IMAGES).mkdir(parents=True, exist_ok=True)
    with open(f"{PATH_IMAGES}/{filename}", "wb") as file:
        file.write(response.content)


if __name__ == "__main__":
    url_image = "https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg"
    filename = "hubble.jpeg"
    download_image(url_image, filename)