from fastapi import FastAPI
import os
from supabase import create_client, Client

app = FastAPI()

SUPABASE_URL = "https://ruvdlcgsmtwszxsposjt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1dmRsY2dzbXR3c3p4c3Bvc2p0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODMxNjQ4MzksImV4cCI6MjA5ODc0MDgzOX0.V_nFon6WsICyaiiN1bujrg5P9ORKb8-L1eMBlCFKZF8"
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
