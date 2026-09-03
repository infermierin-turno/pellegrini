import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from shopify_agent import ShopifyCoffeeAgent

app = FastAPI()

@app.get("/")
def preview_shopify_descriptions():
    shop_url = os.getenv("SHOP_URL")
    client_id = os.getenv("SHOPIFY_CLIENT_ID")
    client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not shop_url or not client_id or not client_secret or not openai_api_key:
        return HTMLResponse("<h3>[ERRORE] Mancano una o più variabili d'ambiente richieste.</h3>")

    agent = ShopifyCoffeeAgent(
        shop_url=shop_url,
        client_id=client_id,
        client_secret=client_secret,
        openai_api_key=openai_api_key
    )

    # Recuperiamo i prodotti e filtriamo quelli senza tag
    products = agent.get_products(limit=10)
    if not products:
        return HTMLResponse("<h3>[AVVISO] Nessun prodotto trovato su Shopify.</h3>")

    tag_filtro = "Ottimizzato IA"
    prodotti_da_elaborare = []

    for product in products:
        tags_raw = product.get("tags", "")
        tags_list = [t.strip() for t in tags_raw.split(",")] if isinstance(tags_raw, str) else (tags_raw or [])
        if tag_filtro not in tags_list:
            prodotti_da_elaborare.append(product)

    if not prodotti_da_elaborare:
        return HTMLResponse("<h3>[AVVISO] Tutti i prodotti analizzati hanno già il tag 'Ottimizzato IA'!</h3>")

    # Prendiamo i primi 3 da mostrare in anteprima
    batch = prodotti_da_elaborare[:3]

    # Costruiamo la pagina HTML con le colonne affiancate
    html_content = """
    <html>
        <head>
            <title>Anteprima Ottimizzazione IA Shopify</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; color: #333; }
                .product-box { background: #fff; border: 1px solid #ddd; padding: 25px; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
                h2 { color: #b91c1c; font-size: 20px; }
                .preview-section { display: flex; gap: 20px; margin-top: 15px; }
                .column { flex: 1; background: #fdfdfd; border: 1px solid #eee; padding: 15px; border-radius: 6px; overflow-x: auto; }
                .column h4 { margin-top: 0; color: #555; border-bottom: 2px solid #ddd; padding-bottom: 8px; }
            </style>
        </head>
        <body>
            <h1>Anteprima Modifiche IA (Modalità Test - Nessuna modifica salvata)</h1>
    """

    for product in batch:
        product_id = product.get("id")
        title = product.get("title")
        current_body = product.get("body_html", "")
        
        # Genera la descrizione ottimizzata tramite IA
        raw_optimized = agent.optimize_coffee_description(title, current_body)
        
        # Pulizia di eventuali blocchi ```html ... ``` restituiti dall'IA
        cleaned_html = raw_optimized.replace("```html", "").replace("```", "").strip()

        html_content += f"""
            <div class="product-box">
                <h2>{title} (ID: {product_id})</h2>
                <div class="preview-section">
                    <div class="column">
                        <h4>Descrizione Attuale</h4>
                        <div>{current_body if current_body else '<em>Nessuna descrizione presente</em>'}</div>
                    </div>
                    <div class="column">
                        <h4>Nuova Anteprima Generata dall'IA</h4>
                        <div>{cleaned_html}</div>
                    </div>
                </div>
            </div>
        """

    html_content += """
        </body>
    </html>
    """

    return HTMLResponse(content=html_content)
