import json
import os

# Mengambil path folder utama (naik 1 level dari folder services/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

def baca_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

def simpan_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)