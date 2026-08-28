from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, Union, List
from datetime import datetime
from email.message import EmailMessage
import smtplib
from supabase import create_client, Client

app = FastAPI()

SUPABASE_URL = "https://ruvdlcgsmtwszxsposjt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1dmRsY2dzbXR3c3p4c3Bvc2p0Iiwicm9sZSI6InJ1dmRsY2dzbXR3c3p4c3Bvc2p0Iiwicm9sZSI6InJ1dmRsY2dzbXR3c3p4c3Bvc2p0Iiwicm9sZSI6InJ1dmRsY2dzbXR3c3p4c3Bvc2p0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODMxNjQ4MzksImV4cCI6MjA5ODc0MDgzOX0.V_nFon6WsICyaiiN1bujrg5P9ORKb8-L1eMBlCFKZF8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurazione SMTP per l'invio delle email direttamente da Python
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "udr.pellegrini@aslnapoli1centro.it"
SMTP_PASSWORD = "Trasfusionale041"
EMAIL_COT = "giovanni.dente@aslnapoli1centro.it"

def invia_email_smtp(oggetto: str, corpo: str):
    msg = EmailMessage()
    msg.set_content(corpo)
    msg['Subject'] = oggetto
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_COT
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Errore invio email SMTP: {str(e)}")

@app.get("/")
def home():
    return {"status": "online"}

@app.get("/analizza-scorte")
def analizza_scorte():
    try:
        response = supabase.table("emoteca_scorte").select("*").eq("stato", "Disponibile").execute()
        sacche = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    critiche = []
    for sacca in sacche:
        gruppo = sacca.get("gruppo_sanguigno", "").strip()
        
        if gruppo == "0 Negativo":
            critiche.append({
                "id": sacca["id"],
                "gruppo_sanguigno": gruppo,
                "priorita": "Massima",
                "messaggio": "Sacca universale critica (0 Negativo) - Priorità massima di utilizzo"
            })
        elif gruppo == "AB Negativo":
            critiche.append({
                "id": sacca["id"],
                "gruppo_sanguigno": gruppo,
                "priorita": "Alta",
                "messaggio": "Gruppo raro (AB Negativo) - Monitorare scorte limitate"
            })
            
    return {
        "stato": "successo",
        "totale_analizzate": len(sacche),
        "sacche_critiche": critiche
    }

class BookingPayload(BaseModel):
    reparto: Union[str, List[str]]
    orario_invio: Optional[str] = None
    note: Optional[str] = None
    urgenza: Optional[str] = "Ordinaria"

@app.post("/ricevi-booking")
def ricevi_booking(payload: BookingPayload, response: Response):
    reparto_val = payload.reparto
    if isinstance(reparto_val, list):
        reparto_pulito = reparto_val[0].strip() if reparto_val else ""
    else:
        reparto_pulito = reparto_val.strip()
        
    if not reparto_pulito:
        response.status_code = 400
        return "Errore Dati - Campo reparto mancante"
        
    orario_input = payload.orario_invio if payload.orario_invio else datetime.now().strftime("%H:%M")
    
    try:
        parti_ora = orario_input.split(":")
        ora = int(parti_ora[0])
        minuti = int(parti_ora[1])
    except (ValueError, IndexError):
        ora, minuti = datetime.now().hour, datetime.now().minute
        
    minuti_totali = (ora * 60) + minuti
    
    turno_calcolato = "Pomeriggio" if 480 <= minuti_totali <= 750 else "Notte"
    urgenza_input = payload.urgenza if payload.urgenza else "Ordinaria"
    
    dati_da_inserire = {
        "reparto": reparto_pulito,
        "turno_successivo": turno_calcolato,
        "note": f"[{urgenza_input}] " + (payload.note if payload.note else ""),
        "stato": "Da ritirare",
        "notifica_inviata": False
    }
    
    try:
        res = supabase.table("ritiri_sangue").insert(dati_da_inserire).execute()
        
        # Se è Urgentissima, Python spedisce subito la mail senza toccare Power Automate
        if urgenza_input.lower() == "urgentissima":
            corpo_mail = f"URGENTISSIMA!\nReparto: {reparto_pulito}\nOrario: {orario_input}\nNote: {payload.note}"
            invia_email_smtp(f"URGENZA SANGUE - {reparto_pulito}", corpo_mail)
            
        response.status_code = 200
        return {
            "status": "OK",
            "turno": turno_calcolato,
            "urgenza": urgenza_input,
            "azione_immediata": True if urgenza_input.lower() == "urgentissima" else False
        }
    except Exception as e:
        response.status_code = 500
        return f"Errore DB - {str(e)}"

@app.get("/preleva-accumulo-mattina")
def preleva_accumulo_mattina():
    try:
        response = supabase.table("ritiri_sangue").select("*").eq("notifica_inviata", False).execute()
        richieste = response.data
        
        if not richieste:
            return {"status": "ok", "totale": 0, "richieste": []}
            
        ids = [r["id"] for r in richieste]
        supabase.table("ritiri_sangue").update({"notifica_inviata": True}).in_("id", ids).execute()
        
        # Genera e invia la mail cumulativa della mattina
        corpo = "Riepilogo richieste ordinarie (Mattina):\n\n"
        for r in richieste:
            corpo += f"- Reparto: {r['reparto']} | Note: {r['note']}\n"
        
        invia_email_smtp("Riepilogo Cumulativo Mattina - Ritiri Sangue", corpo)
        
        return {
            "status": "ok",
            "totale": len(richieste),
            "richieste": richieste
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/preleva-accumulo-pomeriggio")
def preleva_accumulo_pomeriggio():
    try:
        response = supabase.table("ritiri_sangue").select("*").eq("notifica_inviata", False).execute()
        richieste = response.data
        
        if not richieste:
            return {"status": "ok", "totale": 0, "richieste": []}
            
        ids = [r["id"] for r in richieste]
        supabase.table("ritiri_sangue").update({"notifica_inviata": True}).in_("id", ids).execute()
        
        # Genera e invia la mail cumulativa del pomeriggio (furgone ore 16:30)
        corpo = "Riepilogo richieste ordinarie (Pomeriggio - Necessario furgone ore 16:30):\n\n"
        for r in richieste:
            corpo += f"- Reparto: {r['reparto']} | Note: {r['note']}\n"
        
        invia_email_smtp("Riepilogo Cumulativo Pomeriggio - Furgone ore 16:30", corpo)
        
        return {
            "status": "ok",
            "totale": len(richieste),
            "richieste": richieste
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
