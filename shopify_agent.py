import os
import requests
from openai import OpenAI

class ShopifyCoffeeAgent:
    def __init__(self, shop_url, client_id, client_secret, openai_api_key):
        self.shop_url = shop_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.ai_client = OpenAI(api_key=openai_api_key)
        self.access_token = self._get_admin_access_token()
        
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token if self.access_token else ""
        }

    def _get_admin_access_token(self):
        """Ottiene dinamicamente il token di accesso admin usando Client ID e Client Secret."""
        auth_url = f"{self.shop_url}/admin/oauth/access_token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            # Tentativo di richiesta del token con le credenziali dell'app
            response = requests.post(auth_url, data=payload)
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print("[SUCCESSO] Token di accesso Shopify generato correttamente.")
                return token
            else:
                print(f"[AVVISO] OAuth standard non riuscito ({response.status_code}: {response.text}).")
                print("Tentativo di fallback con autenticazione diretta o credenziali custom...")
                return self._fallback_token_request()
        except Exception as e:
            print(f"Errore durante la richiesta del token Shopify: {e}")
            return None

    def _fallback_token_request(self):
        """Metodo di supporto nel caso in cui l'endpoint richieda una struttura di scambio differente."""
        # Se usi le credenziali della Dev Dashboard, a volte l'app richiede un token di accesso 
        # generato direttamente dall'interfaccia o tramite Basic Auth.
        # Restituiamo il client_secret come fallback se configurato come password temporanea.
        return self.client_secret

    def get_products(self, limit=5):
        """Recupera l'elenco dei prodotti dal negozio Shopify."""
        url = f"{self.shop_url}/admin/api/2024-01/products.json?limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get("products", [])
        else:
            print(f"Errore nel recupero prodotti: {response.status_code} - {response.text}")
            return []

    def optimize_coffee_description(self, title, current_body):
        """Usa l'IA per trasformare la descrizione in un testo persuasivo e ottimizzato SEO per il caffè."""
        prompt = f"""
        Sei un copywriter esperto e un sommelier del caffè. 
        Ottimizza la seguente descrizione del prodotto per un e-commerce di caffè di alta qualità.
        
        Nome Prodotto: {title}
        Descrizione Attuale: {current_body}
        
        Requisiti:
        - Scrivi una descrizione accattivante, incentrata sulle note aromatiche, sul profilo di tostatura e sull'esperienza di degustazione.
        - Includi una struttura pulita con brevi punti elenco (es. Intensità, Origine, Ideale per).
        - Restituisci il testo in formato HTML di base (es. <p>, <ul>, <li>, <strong>) pronto per essere inserito su Shopify.
        """

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Errore durante la chiamata IA: {e}")
            return current_body

    def update_product_description(self, product_id, new_body_html):
        """Aggiorna la descrizione del prodotto su Shopify."""
        url = f"{self.shop_url}/admin/api/2024-01/products/{product_id}.json"
        payload = {
            "product": {
                "id": product_id,
                "body_html": new_body_html
            }
        }
        response = requests.put(url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            print(f"[SUCCESSO] Prodotto ID {product_id} aggiornato con successo.")
            return True
        else:
            print(f"[ERRORE] Impossibile aggiornare il prodotto {product_id}: {response.text}")
            return False

    def run_optimization_pipeline(self, limit=3):
        """Esegue il flusso completo: legge i prodotti, li ottimizza con l'IA e li aggiorna."""
        print("Avvio della pipeline IA per Shopify...")
        products = self.get_products(limit=limit)
        
        if not products:
            print("Nessun prodotto trovato o errore di connessione.")
            return

        for product in products:
            prod_id = product["id"]
            title = product["title"]
            body_html = product.get("body_html", "")
            
            print(f"\nElaborazione in corso per: '{title}'...")
            
            # Genera il nuovo contenuto ottimizzato tramite IA
            optimized_html = self.optimize_coffee_description(title, body_html)
            
            # Esegue l'update su Shopify
            self.update_product_description(prod_id, optimized_html)
