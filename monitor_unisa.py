import requests
from bs4 import BeautifulSoup
import json
import os

# Legge credenziali dai secrets GitHub
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

PAGES = {
    "Dipartimento SUM": "https://www.dipsum.unisa.it/home/news",
    "Linguistica e didattica dell’italiano": "https://corsi.unisa.it/linguistica-e-didattica-dell-italiano/comunicazioni-docenti",
    "Filologia, letterature e storia dell’antichità": "https://corsi.unisa.it/filologia-letterature-e-storia-dell-antichita/comunicazioni-docenti",
    "Filologia moderna": "https://corsi.unisa.it/filologia-moderna/comunicazioni-docenti",
}

SEEN_FILE = "seen.json"

def load_seen():
    """Carica i link già inviati da file"""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            try:
                return set(json.load(f))
            except:
                return set()
    return set()

def save_seen(seen):
    """Salva i link già inviati"""
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def estrai_news(url):
    """Estrae notizie (titolo, link) dalle varie pagine"""
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    news = []

    # Caso 1: Dipartimento SUM
    for item in soup.select("div.elenco-comunicati li a"):
        titolo = item.get_text(strip=True)
        link = item.get("href")
        if not link.startswith("http"):
            link = "https://www.dipsum.unisa.it" + link
        news.append((titolo, link))

    # Caso 2: Comunicazioni-docenti corsi di laurea
    for item in soup.select("div#comunicatiDocente li a"):
        titolo = item.get_text(strip=True)
        link = item.get("href")
        if not link.startswith("http"):
            base = "/".join(url.split("/")[:3])  # es. https://corsi.unisa.it
            link = base + link
        news.append((titolo, link))

    return news

def send_telegram(text):
    """Manda un messaggio Telegram al bot"""
    if not TOKEN or not CHAT_ID:
        print("❌ Errore: manca TELEGRAM_TOKEN o TELEGRAM_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })

if __name__ == "__main__":
    seen = load_seen()

    for nome, url in PAGES.items():
        notizie = estrai_news(url)
        for titolo, link in notizie[:3]:  # controlla solo le ultime 3 notizie
            if link not in seen:
                msg = f"📢 {nome}\n📰 {titolo}\n🔗 {link}"
                send_telegram(msg)
                seen.add(link)

    save_seen(seen)
