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

    # ATTENZIONE: Mettendo dry_run=True, l'IA genera i testi e te li mostra nei log 
    # SENZA scriverli su Shopify. Quando sei soddisfatto, basterà rimettere False.
    print("[INFO] Avvio della pipeline in modalità ANTEPRIMA (Dry-Run)...")
    agent.run_optimization_pipeline(limit=4, dry_run=True)

if __name__ == "__main__":
    main()
