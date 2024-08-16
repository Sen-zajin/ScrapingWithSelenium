import json
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://api-2.pmahrm.com/api/curriculum_updates"
items_per_page = 20
all_candidates = []  # Lista per memorizzare tutti i candidati
retry_delay = 10

def get_token(session, url):
    raw = session.get(url).text
    token = raw[raw.index("token")+8:]
    token = token[:token.index("\"")]
    return f"Bearer {token}"

def setup_selenium():
    edge_options = Options()
    edge_options.add_argument("--headless")  # Esegui Edge in modalità headless
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=edge_options)
    return driver

def simulate_human_interaction(driver, curriculum_id, headers):
    page = 1

    while True:
        # Simula la navigazione dell'utente
        params = {
            'itemsPerPage': items_per_page,
            'page': page,
            'order[id]': 'desc',
            'curriculum': f'/api/curricula/{curriculum_id}',
            'isManual': ''
        }

        url = base_url + '?' + '&'.join(f'{k}={v}' for k, v in params.items())
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//script[@type="application/json"]'))
            )

            time.sleep(random.uniform(1, 5))  # Pausa casuale per dare il tempo alla pagina di caricarsi

            data = download_data_with_requests(params, headers)
            if not data:
                print("Nessun altro dato da scaricare.")
                break

            all_candidates.extend(data)
            page += 1  # Vai alla pagina successiva

        except Exception as e:
            print(f"Errore durante il caricamento della pagina o l'elaborazione dei dati: {e}")
            break

    driver.quit()

def download_data_with_requests(params, headers):
    try:
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('candidates', [])
        else:
            print(f"Errore durante la richiesta: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Errore nella richiesta API: {e}")
        return []

# Funzione principale
def main():
    session = requests.session()
    token_url = "https://api-2.performahrm.com"  # URL per ottenere il token (da aggiornare)
    headers = {
        'Accept-Encoding': 'gzip',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Authorization': get_token(session, token_url)
    }
    
    curriculum_id = 8558157  # Inserisci l'ID del curriculum desiderato
    driver = setup_selenium()
    
    simulate_human_interaction(driver, curriculum_id, headers)

    # Salva i dati in un file JSON
    with open('candidati.json', 'w') as f:
        json.dump(all_candidates, f, indent=4)

    print(f"Scaricati {len(all_candidates)} candidati.")

# Avvia il programma
if __name__ == "__main__":
    main()
