import hashlib
import os
import requests

PDF_URL = "https://www.ghc.com.br/portalrh/files/arq_ptg_6_1_2463.pdf"
HASH_FILE = "last_hash.txt"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Credenciais do Telegram ausentes.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def check_update():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(PDF_URL, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"Erro ao acessar URL: Status {response.status_code}")
        return

    # Calcula a assinatura única do PDF atual
    current_hash = hashlib.md5(response.content).hexdigest()

    # Lê o hash gravado anteriormente
    last_hash = ""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            last_hash = f.read().strip()

    if current_hash != last_hash:
        print("Mudança detectada ou primeira execução!")
        with open(HASH_FILE, "w") as f:
            f.write(current_hash)

        # Se não for a primeira execução, dispara o alerta
        if last_hash != "":
            send_telegram_alert(
                f"🚨 *Atenção: O arquivo PDF do GHC foi alterado!*\n\n"
                f"Acesse o arquivo atualizado aqui:\n{PDF_URL}"
            )
    else:
        print("Sem alterações no arquivo.")

if __name__ == "__main__":
    check_update()
