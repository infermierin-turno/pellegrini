from fastapi import FastAPI
import os
from supabase import create_client, Client

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/analizza-scorte")
def analizza_scorte():
    response = supabase.table("emoteca_scorte").select("*").eq("stato", "Disponibile").execute()
    sacche = response.data
    
    critiche = []
    for sacca in sacche:
        if sacca.get("gruppo_sanguigno") == "0 Negativo":
            critiche.append({
                "id": sacca["id"],
                "messaggio": "Sacca universale critica - Priorità massima di utilizzo"
            })
            
    return {
        "stato": "successo",
        "totale_analizzate": len(sacche),
        "sacche_critiche": critiche
    }
