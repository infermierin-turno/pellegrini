from shopify_agent import ShopifyCoffeeAgent

# Le tue credenziali reali per l'e-commerce di caffè
SHOP_URL = "https://tuo-negozio.myshopify.com"
SHOPIFY_ACCESS_TOKEN = "shpat_il_tuo_token_privato_shopify"
OPENAI_API_KEY = "sk-la_tua_chiave_openai"

def main():
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
