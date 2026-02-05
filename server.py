from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "APO Tracker API działa"

@app.route("/player/<name>")
def player(name):
    url = f"https://armia.toproste.pl/player-{name}.html"

    try:
        r = requests.get(url, timeout=10, verify=False)
        r.raise_for_status()
    except Exception:
        return jsonify({"error": "Nie udało się pobrać strony"}), 500

    soup = BeautifulSoup(r.text, "html.parser")

    # ===== ZBIERAMY WSZYSTKIE PARY LABEL → VALUE =====
    data = {}

    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).replace(":", "")
            value = cells[1].get_text(strip=True)
            data[label] = value

    # ===== WYCIĄGANIE DANYCH =====
    def to_int(val, default=0):
        if not val:
            return default
        val = val.replace(" ", "").replace(",", "")
        return int(re.findall(r"\d+", val)[0]) if re.findall(r"\d+", val) else default

    level = to_int(data.get("Poziom"), 1)
    magic = to_int(data.get("Poziom magiczny"), 0)
    experience = to_int(data.get("Doświadczenie"), 0)
    vocation = data.get("Profesja", "Rook")

    return jsonify({
        "name": name,
        "level": level,
        "magic": magic,
        "experience": experience,
        "vocation": vocation
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
