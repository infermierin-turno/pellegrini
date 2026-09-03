import os
from shopify_agent import ShopifyCoffeeAgent

def main():
    shop_url = os.getenv("SHOP_URL")
    client_id = os.getenv("SHOPIFY_CLIENT_ID")
    client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not shop_url or not client_id or not client_secret or not openai_api_key:
        print("[ERRORE] Mancano una o più variabili d'ambiente richieste.")
        return

    agent = ShopifyCoffeeAgent(
        shop_url=shop_url,
        client_id=client_id,
        client_secret=client_secret,
        openai_api_key=openai_api_key
    )

    # Recuperiamo un blocco più ampio per trovare i prodotti non ancora ottimizzati
    limit = 10
    print(f"[INFO] Recupero dei prodotti da Shopify per verificare i tag...")
    
    products = agent.get_products(limit=limit)
    
    if not products:
        print("[AVVISO] Nessun prodotto trovato.")
        return

    # Filtriamo solo i prodotti che NON hanno il tag "Ottimizzato IA"
    tag_filtro = "Ottimizzato IA"
    prodotti_da_elaborare = []

    for product in products:
        tags_raw = product.get("tags", "")
        # Shopify restituisce i tag come stringa separata da virgole o come lista a seconda della versione
        if isinstance(tags_raw, str):
            tags_list = [t.strip() for t in tags_raw.split(",")]
        else:
            tags_list = tags_raw or []

        if tag_filtro not in tags_list:
            prodotti_da_elaborare.append(product)

    if not prodotti_da_elaborare:
        print("[AVVISO] Tutti i prodotti recuperati hanno già il tag 'Ottimizzato IA'. Nessun nuovo articolo da elaborare.")
        return

    # Limitiamo l'elaborazione ad esempio a 3 prodotti alla volta per ogni esecuzione
    batch_da_processare = prodotti_da_elaborare[:3]
    print(f"[INFO] Trovati {len(batch_da_processare)} prodotti da elaborare in questa sessione.")

    for product in batch_da_processare:
        product_id = product.get("id")
        title = product.get("title")
        current_body = product.get("body_html", "")
        
        print(f"\n--- PRODOTTO SELEZIONATO ---")
        print(f"ID: {product_id}")
        print(f"Titolo: {title}")
        
        # Generiamo la descrizione ottimizzata tramite IA
        optimized_description = agent.optimize_coffee_description(title, current_body)
        print(f"---> NUOVA DESCRIZIONE GENERATA DALL'IA:\n{optimized_description}\n")

    print("==================================================")
    print("[MODALITÀ ANTEPRIMA COMPLETATA] Nessuna modifica scritta su Shopify.")
    print("I prodotti sopra mostrati non hanno ancora il tag e verranno saltati solo dopo che sarai tu a confermare e applicare il tag.")

if __name__ == "__main__":
    main()
