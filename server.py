from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import urllib3
import os
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# ===== CACHE =====
CACHE = {}
CACHE_TTL = 60   # sekundy

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/player/<name>")
def player(name):
    now = time.time()

    # CACHE
    if name in CACHE and now - CACHE[name]["time"] < CACHE_TTL:
        return jsonify(CACHE[name]["data"])

    url = f"https://armia.toproste.pl/player-{name}.html"

    try:
        r = requests.get(url, timeout=10, verify=False)
        r.raise_for_status()
    except Exception:
        return jsonify({"error": "Nie udało się pobrać strony"}), 500

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    def extract_int(pattern, default=0):
        m = re.search(pattern, text)
        return int(m.group(1)) if m else default

    def extract_str(pattern, default="Rook"):
        m = re.search(pattern, text)
        return m.group(1).strip() if m else default

    level = extract_int(r"Poziom:\s*(\d+)", 1)
    magic = extract_int(r"Poziom magiczny:\s*(\d+)", 0)
    experience = extract_int(r"Doświadczenie:\s*(\d+)", 0)

    vocation = extract_str(
    r"Profesja:\s*(Rycerz|Paladyn|Druid|Czarodziej|Rook|Brak)",
    "Rook"
)

    )

    if vocation.lower() in ["brak", "rook"]:
    vocation = "Rook"


    data = {
        "name": name,
        "level": level,
        "magic": magic,
        "experience": experience,
        "vocation": vocation
    }

    CACHE[name] = {
        "time": now,
        "data": data
    }

    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

