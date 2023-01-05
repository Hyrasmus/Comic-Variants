import hashlib
import pendulum
import requests
from flask import Flask, render_template, request

from keys import PRIVATE_KEY, PUBLIC_KEY

app = Flask(__name__)

def get_character(PUBLIC_KEY, PRIVATE_KEY, name):
    # Generate timestamp required for Marvel API Authentication.
    now = pendulum.now('Europe/London')
    now = now.to_iso8601_string()

    # Generate hash required for Marvel API Authentication.
    m = hashlib.md5()
    m.update(now.encode('utf8'))
    m.update(PRIVATE_KEY.encode('utf8'))
    m.update(PUBLIC_KEY.encode('utf8'))

    endpoint = f"https://gateway.marvel.com:443/v1/public/characters?nameStartsWith={name}&limit=1"
    resp = requests.get(endpoint, params={"apikey": PUBLIC_KEY, "ts": now, "hash": m.hexdigest()}).json()
    # Collect required data from resp.
    try:
        name = resp["data"]["results"][0]["name"]
        description = resp["data"]["results"][0]["description"]
        thumbnail = resp["data"]["results"][0]["thumbnail"]["path"]
        extension = resp["data"]["results"][0]["thumbnail"]["extension"]
        thumbnail = f"{thumbnail}.{extension}"
        return {"name": name, "description": description, "thumbnail": thumbnail}
    except Exception as e:
        return None

def get_comics(PUBLIC_KEY, PRIVATE_KEY, name):
    # Generate timestamp required for Marvel API Authentication.
    now = pendulum.now('Europe/London')
    now = now.to_iso8601_string()

    # Generate hash required for Marvel API Authentication.
    m = hashlib.md5()
    m.update(now.encode('utf8'))
    m.update(PRIVATE_KEY.encode('utf8'))
    m.update(PUBLIC_KEY.encode('utf8'))

    endpoint = f"https://gateway.marvel.com:443/v1/public/comics?titleStartsWith={name}&limit=1"
    resp = requests.get(endpoint, params={"apikey": PUBLIC_KEY, "ts": now, "hash": m.hexdigest()}).json()
    # Collect required data from resp.
    try:
        title = resp["data"]["results"][0]["title"]
        image_path = resp["data"]["results"][0]["thumbnail"]["path"]
        image_extension = resp["data"]["results"][0]["thumbnail"]["extension"]
        image_url = f"{image_path}.{image_extension}"
        return {"title": title, "image_url": image_url}
    except Exception as e:
        return None


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["search"]
        data = get_character(PUBLIC_KEY, PRIVATE_KEY, name)
        return render_template("index.html", data=data)
    
    return render_template("index.html")

@app.route('/comic/', methods=["GET", "POST"])
def comic():
    if request.method == "POST":
        name = request.form["search"]
        comics = get_comics(PUBLIC_KEY, PRIVATE_KEY, name)
        return render_template("comic.html", comics=comics)
    return render_template("comic.html")


if __name__ == '__main__':
   app.run()
