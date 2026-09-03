import os
from shopify_agent import ShopifyCoffeeAgent

# Legge le credenziali in modo sicuro dalle variabili d'ambiente impostate su Render
SHOP_URL = os.getenv("SHOP_URL", "https://348aca-2.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
