import requests


if __name__ == "__main__":
    url_all = "https://api.spacexdata.com/v4/launches"

    response = requests.get(url_all)
    response.raise_for_status()
    launches = response.json()
    for launch in launches[::-1]:
        images = launch["links"]["flickr"]["original"]
        if images:
            break
    
    print(*images, sep='\n')
