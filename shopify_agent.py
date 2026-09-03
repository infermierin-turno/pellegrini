import os
from shopify_agent import ShopifyCoffeeAgent

def main():
    # Recupera le variabili d'ambiente corrette
    shop_url = os.getenv("SHOP_URL")
    client_id = os.getenv("SHOPIFY_CLIENT_ID")
    client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Verifica di sicurezza sulle chiavi necessarie
    if not shop_url or not client_id or not client_secret or not openai_api_key:
        print("[ERRORE] Mancano una o più variabili d'ambiente richieste (SHOP_URL, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET, OPENAI_API_KEY).")
        return

    # Inizializza l'agente con le credenziali OAuth
    agent = ShopifyCoffeeAgent(
        shop_url=shop_url,
        client_id=client_id,
        client_secret=client_secret,
        openai_api_key=openai_api_key
    )

    # Esegue l'ottimizzazione sui primi prodotti del catalogo
    agent.run_optimization_pipeline(limit=3)

if __name__ == "__main__":
    main()
