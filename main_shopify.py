import os
from shopify_agent import ShopifyCoffeeAgent

agent = ShopifyCoffeeAgent(
    shop_url=os.getenv("SHOPIFY_SHOP_URL"),
    client_id=os.getenv("SHOPIFY_CLIENT_ID"),
    client_secret=os.getenv("SHOPIFY_CLIENT_SECRET"),
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def main():
    # Verifica di sicurezza sulle chiavi
    if not SHOPIFY_ACCESS_TOKEN or not OPENAI_API_KEY:
        print("[ERRORE] Mancano le chiavi SHOPIFY_ACCESS_TOKEN o OPENAI_API_KEY nelle variabili d'ambiente.")
        return

    # Inizializza l'agente
    agent = ShopifyCoffeeAgent(
        shop_url=SHOP_URL,
        access_token=SHOPIFY_ACCESS_TOKEN,
        openai_api_key=OPENAI_API_KEY
    )
    
    # Esegue l'ottimizzazione sui primi prodotti del catalogo
    agent.run_optimization_pipeline(limit=3)

if __name__ == "__main__":
    main()
