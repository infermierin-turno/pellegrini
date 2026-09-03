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

    limit = 3
    print(f"[INFO] Recupero dei primi {limit} prodotti da Shopify per l'anteprima...")
    
    products = agent.get_products(limit=limit)
    
    if not products:
        print("[AVVISO] Nessun prodotto trovato.")
        return

    for product in products:
        product_id = product.get("id")
        title = product.get("title")
        current_body = product.get("body_html", "")
        
        print(f"\n--- PRODOTTO SELEZIONATO ---")
        print(f"ID: {product_id}")
        print(f"Titolo: {title}")
        
        # Generiamo la descrizione ottimizzata tramite IA usando il metodo corretto
        optimized_description = agent.optimize_coffee_description(title, current_body)
        print(f"---> NUOVA DESCRIZIONE GENERATA DALL'IA:\n{optimized_description}\n")

    print("==================================================")
    print("[MODALITÀ ANTEPRIMA COMPLETATA] Nessuna modifica scritta su Shopify.")

if __name__ == "__main__":
    main()
