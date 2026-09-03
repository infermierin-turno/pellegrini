import os
import requests
from openai import OpenAI

class ShopifyCoffeeAgent:
    def __init__(self, shop_url, client_id, client_secret, openai_api_key):
        self.shop_url = shop_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.ai_client = OpenAI(api_key=openai_api_key)
        
        # Genera il token di accesso usando le credenziali OAuth
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
            response = requests.post(auth_url, data=payload)
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print("[SUCCESSO] Token di accesso Shopify generato correttamente.")
                return token
            else:
                print(f"[AVVISO] OAuth standard non riuscito ({response.status_code}: {response.text}).")
                return self.client_secret
        except Exception as e:
            print(f"Errore durante la richiesta del token Shopify: {e}")
            return None

    def get_products(self, limit=20):
        """Recupera l'elenco dei prodotti dal negozio Shopify."""
        url = f"{self.shop_url}/admin/api/2024-01/products.json?limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get("products", [])
        else:
            print(f"Errore nel recupero prodotti: {response.status_code} - {response.text}")
            return []

    def optimize_coffee_description(self, title, current_body):
        """Usa l'IA per trasformare la descrizione in un testo persuasivo e ottimizzato SEO."""
        system_prompt = """
Sei il copywriter e l'esperto ufficiale di Caffè Sansone, una torrefazione artigianale italiana. 
La tua voce è italiana, esperta, cordiale e concreta: artigianale senza essere pomposa, precisa senza essere rigida. Aiuti chi visita lo shop a scegliere, capire e risolvere velocemente, parlando a persone che cercano caffè specialty, miscele per espresso e moka, monorigine e formati pratici. Si sente la cura da micro-torrefazione e l’attenzione per il caffè fatto bene.

REGOLE TASSATIVE:
1. Restituisci ESCLUSIVAMENTE codice HTML puro (strutturato con tag come <h2>, <p>, <ul>, <li>, <strong>, ecc.).
2. VIETATO inserire frasi introduttive, commenti o chiacchiere (es. "Ecco la descrizione...", "Certamente!").
3. VIETATO aggiungere i blocchi di markdown ```html o ``` attorno al codice. Restituisci solo il testo HTML grezzo e pulito, pronto per essere salvato su Shopify.
4. Mantieni sempre tutti i dati tecnici reali del prodotto (peso, percentuali di blend, formati, compatibilità e note di spedizione) senza inventare dati non veritieri.
"""

        user_prompt = f"""
Ottimizza la seguente descrizione del prodotto per il nostro e-commerce di caffè.
        
Nome Prodotto: {title}
Descrizione Attuale: {current_body}
        
Requisiti:
- Scrivi una descrizione accattivante, incentrata sulle note aromatiche, sul profilo di tostatura e sull'esperienza di degustazione.
- Includi una struttura pulita con brevi punti elenco (es. Intensità, Origine, Ideale per).
- Restituisci esclusivamente il codice HTML pulito secondo le istruzioni di sistema.
"""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Errore durante la chiamata IA: {e}")
            return current_body

    def update_product_description_and_tag(self, product_id, new_body_html, tag_to_add="Ottimizzato IA"):
        """Aggiorna la descrizione del prodotto su Shopify e aggiunge il tag per evitare duplicazioni."""
        get_url = f"{self.shop_url}/admin/api/2024-01/products/{product_id}.json"
        get_resp = requests.get(get_url, headers=self.headers)
        
        current_tags_str = ""
        if get_resp.status_code == 200:
            product_data = get_resp.json().get("product", {})
            current_tags_str = product_data.get("tags", "")

        tags_list = [t.strip() for t in current_tags_str.split(",")] if current_tags_str else []
        if tag_to_add not in tags_list:
            tags_list.append(tag_to_add)
        
        updated_tags_str = ", ".join(tags_list)

        put_url = f"{self.shop_url}/admin/api/2024-01/products/{product_id}.json"
        payload = {
            "product": {
                "id": product_id,
                "body_html": new_body_html,
                "tags": updated_tags_str
            }
        }
        
        response = requests.put(put_url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            print(f"[SUCCESSO] Prodotto ID {product_id} aggiornato e taggato con successo.")
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
            optimized_html = self.optimize_coffee_description(title, body_html)
            self.update_product_description_and_tag(prod_id, optimized_html, tag_to_add="Ottimizzato IA")
