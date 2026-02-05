from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/player/<name>")
def player(name):
    url = f"https://armia.toproste.pl/player-{name}.html"
    r = requests.get(url, timeout=10, verify=False)

    if r.status_code != 200:
        return jsonify({"error": "Nie udało się pobrać danych postaci"}), 500

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    level = int(re.search(r"Poziom:\s*(\d+)", text).group(1))
    magic = int(re.search(r"Poziom magiczny:\s*(\d+)", text).group(1))
    experience = int(re.search(r"Doświadczenie:\s*(\d+)", text).group(1))

    return jsonify({
        "name": name,
        "level": level,
        "magic": magic,
        "experience": experience
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
