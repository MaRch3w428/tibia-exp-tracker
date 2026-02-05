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

    def get_value(label):
        """
        Szuka w tabeli:
        <td>LABEL</td><td>WARTOŚĆ</td>
        """
        td = soup.find("td", string=re.compile(f"^{label}$", re.I))
        if not td:
            return None
        value_td = td.find_next_sibling("td")
        if not value_td:
            return None
        return value_td.get_text(strip=True)

    try:
        level = int(get_value("Poziom") or 1)
        magic = int(get_value("Poziom magiczny") or 0)

        exp_raw = get_value("Doświadczenie") or "0"
        experience = int(exp_raw.replace(" ", "").replace(",", ""))

        vocation = get_value("Profesja") or "Rook"
    except Exception:
        return jsonify({"error": "Błąd parsowania danych"}), 500

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
