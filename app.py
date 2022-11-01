from urllib3 import connection_from_url


try:
    import hashlib

    import pendulum
    import requests
    from flask import Flask, render_template, request

    from keys import PRIVATE_KEY, PUBLIC_KEY
except ImportError as err:
    print(f"Failed to import required packages: {err}")

def get_character(PUBLIC_KEY, PRIVATE_KEY, id, name):
    # Generate timestamp required for Marvel API Authentication.
    now = pendulum.now('Europe/London')
    now = now.to_iso8601_string()

    # Generate hash required for Marvel API Authentication.
    m = hashlib.md5()
    m.update(now.encode('utf8'))
    m.update(PRIVATE_KEY.encode('utf8'))
    m.update(PUBLIC_KEY.encode('utf8'))

    endpoint = f"https://gateway.marvel.com:443/v1/public/characters?nameStartsWith={name}"
    resp = requests.get(endpoint, params={"apikey": PUBLIC_KEY, "ts": now, "hash": m.hexdigest()}).json()
    # Collect required data from resp.
    try:
        id = resp["data"]["results"]["id"]
        name = resp["data"]["results"]["name"]
        description = resp["data"]["results"]["description"]
        thumbnail = resp["data"]["results"]["thumbnail"]["path"]
        extension = resp["data"]["results"]["thumbnail"]["extension"]
        # Format URL for image from resp.
        thumbnail = f"{thumbnail}/landscape_incredible.{extension}"
        return {"id": id, "name": name, "description": description, "thumbnail": thumbnail}
    except IndexError:
        return render_template("index.html")

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["search"]
        data = get_character(PUBLIC_KEY, PRIVATE_KEY, name)
        return render_template("index.html", data=data)
    
    return render_template("index.html")


if __name__ == '__main__':
   app.run()

