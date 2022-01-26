import requests
from pathlib import Path


PATH_IMAGES = "images"
URL_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg"
FILENAME = "hubble.jpeg"

if __name__ == "__main__":
    headers = {
        "User-Agent" : "download_picture"
    }
    response = requests.get(URL_IMAGE, headers=headers)
    response.raise_for_status()

    Path(PATH_IMAGES).mkdir(parents=True, exist_ok=True)
    with open(f"{PATH_IMAGES}/{FILENAME}", "wb") as file:
        file.write(response.content)