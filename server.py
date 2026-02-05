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
        if r.status_code != 200:
            return jsonify({"error": "Nie udało się pobrać strony"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    def extract(pattern, default=0):
        m = re.search(pattern, text)
        return int(m.group(1)) if m else default

    level = extract(r"Poziom:\s*(\d+)")
    magic = extract(r"Poziom magiczny:\s*(\d+)")
    experience = extract(r"Doświadczenie:\s*(\d+)")

    # VOCATION
    vocation_match = re.search(r"Profesja:\s*([A-Za-ząćęłńóśżź ]+)", text)
    vocation = vocation_match.group(1).strip() if vocation_match else "Rook"

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
