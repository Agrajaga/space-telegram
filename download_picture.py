import requests


URL_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg"
FILENAME = "hubble.jpeg"

if __name__ == "__main__":

    headers = {
        "User-Agent" : "download_picture"
    }
    response = requests.get(URL_IMAGE, headers=headers)
    response.raise_for_status()

    with open(FILENAME, "wb") as file:
        file.write(response.content)