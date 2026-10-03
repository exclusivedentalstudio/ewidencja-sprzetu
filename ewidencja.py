import streamlit as st
from supabase import create_client, Client
import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Exclusive Dental Studio - System Zasobów",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. POŁĄCZENIE Z SUPABASE ---
# Wklej swoje poprawne dane dostępowe:
SUPABASE_URL = "https://wfcchwwfikmjpevlfnms.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndmY2Nod3dmaWttanBldmxmbm1zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEwMjIwMDIsImV4cCI6MjEwNjU5ODAwMn0.rJbsuf60L46ph-24cnbD4vPfqIaTymrczMzw_Wovp5E"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- STYLE CSS (Ciemny motyw, złote akcenty, nowoczesny wygląd) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    header[data-testid="stHeader"] { display: none; }
    footer { visibility: hidden; }

    .main {
        background-color: #0E1117;
        color: #E0E0E0;
    }

    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%);
        color: #000000;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
    }

    div[data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #161B22;
        padding: 8px;
        border-radius: 12px;
    }

    button[data-baseweb="tab"] {
        border-radius: 8px;
        color: #8B949E;
        font-weight: 500;
    }

    button[aria-selected="true"] {
        background-color: #21262D !important;
        color: #D4AF37 !important;
    }

    .card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- NAGŁÓWEK APLIKACJI ---
st.markdown("""
<div style="text-align: center; padding: 20px 0 30px 0;">
    <h1 style="color: #D4AF37; font-size: 2.5rem; margin-bottom: 5px;">EXCLUSIVE DENTAL STUDIO</h1>
    <p style="color: #8B949E; font-size: 1.1rem;">System Ewidencji Sprzętu i Historii Napraw</p>
</div>
""", unsafe_allow_html=True)

# --- ZAKŁADKI ---
tab_lista, tab_nowy_serwis, tab_historia = st.tabs([
    "📦 Lista i Wyszukiwarka Sprzętu", 
    "🛠️ Wyszlij do Serwisu / Zamknij Naprawę", 
    "📋 Karta Sprzętu i Pełna Historia"
])

# ==========================================
# ZAKŁADKA 1: LISTA SPRZĘTU
# ==========================================
with tab_lista:
    st.subheader("Baza Sprzętu Medycznego")
    szukaj = st.text_input("🔍 Szukaj sprzętu (nazwa, numer seryjny, dostawca):", placeholder="Wpisz nazwę...")
    
    query = supabase.table("sprzet").select("*")
    if szukaj:
        query = query.ilike("nazwa", f"%{szukaj}%")
    
    sprzet_data = query.execute().data
    
    if sprzet_data:
        st.dataframe(sprzet_data, use_container_width=True)
    else:
        st.info("Brak sprzętu spełniającego kryteria.")

# ==========================================
# ZAKŁADKA 2: WYSYŁKA I ODBIÓR Z SERWISU
# ==========================================
with tab_nowy_serwis:
    col_out, col_in = st.columns(2)
    
    # --- WYSYŁKA DO SERWISU ---
    with col_out:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📤 Wysyłka sprzętu do serwisu")
        
        wszystki_sprzet = supabase.table("sprzet").select("id, nazwa, numer_seryjny").execute().data
        
        if wszystki_sprzet:
            wybrany = st.selectbox(
                "Wybierz sprzęt do wysłania:", 
                wszystki_sprzet, 
                format_func=lambda x: f"{x['nazwa']} (SN: {x.get('numer_seryjny') or 'Brak'})",
                key="select_send"
            )
            
            with st.form("form_send_service"):
                firma_serwis = st.text_input("Firma serwisowa (np. EMS, Dentsply, Serwis X):")
                opis_usterki = st.text_area("Opis usterki / Rodzaj naprawy:")
                data_zgl = st.date_input("Data zgłoszenia:", datetime.date.today())
                
                if st.form_submit_button("Wyślij do serwisu"):
                    if firma_serwis:
                        data_serwisu = {
                            "sprzet_id": wybrany["id"],
                            "nazwa_sprzetu": wybrany["nazwa"],
                            "numer_seryjny": wybrany.get("numer_seryjny"),
                            "serwis_firma": firma_serwis,
                            "rodzaj_naprawy": opis_usterki,
                            "data_zgloszenia": str(data_zgl),
                            "status_serwisu": "W naprawie"
                        }
                        supabase.table("serwis").insert(data_serwisu).execute()
                        st.success(f"Zgłoszono naprawę w firmie: {firma_serwis}")
                        st.rerun()
                    else:
                        st.error("Podaj nazwę firmy serwisowej!")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ODBIÓR Z SERWISU ---
    with col_in:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📥 Odbiór z serwisu")
        
        # Pobieramy tylko sprzęty "W naprawie"
        w_naprawie = supabase.table("serwis").select("*").eq("status_serwisu", "W naprawie").execute().data
        
        if w_naprawie:
            do_zamkniecia = st.selectbox(
                "Wybierz sprzęt wracający z serwisu:",
                w_naprawie,
                format_func=lambda x: f"{x['nazwa_sprzetu']} - {x['serwis_firma']} (Zgłoszenie: {x['data_zgloszenia']})",
                key="select_close"
            )
            
            with st.form("form_close_service"):
                data_powrotu = st.date_input("Data powrotu:", datetime.date.today())
                koszt = st.number_input("Koszt naprawy (zł):", min_value=0.0, step=10.0)
                uwagi = st.text_area("Uwagi po naprawie / Co zrobiono:")
                
                if st.form_submit_button("Zatwierdź powrót z serwisu"):
                    data_update = {
                        "status_serwisu": "Naprawiono",
                        "data_powrotu": str(data_powrotu),
                        "koszt_naprawy": koszt,
                        "uwagi_serwisowe": uwagi
                    }
                    supabase.table("serwis").update(data_update).eq("id", do_zamkniecia["id"]).execute()
                    st.success("Zamknięto zgłoszenie serwisowe!")
                    st.rerun()
        else:
            st.info("Brak sprzętu aktualnie znajdującego się w serwisie.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# ZAKŁADKA 3: KARTA SPRZĘTU I HISTORIA
# ==========================================
with tab_historia:
    st.subheader("Karta Sprzętu i Historia Zgłoszeń")
    
    list_all = supabase.table("sprzet").select("id, nazwa, numer_seryjny").execute().data
    
    if list_all:
        wybrany_sprzet = st.selectbox(
            "Wybierz sprzęt z bazy, aby zobaczyć szczegóły i historię:", 
            list_all, 
            format_func=lambda x: f"{x['nazwa']} (SN: {x.get('numer_seryjny') or 'Brak'})",
            key="select_history"
        )
        
        s_id = wybrany_sprzet["id"]
        
        # Pobieramy dane o sprzęcie z bazy
        dane_sprzetu = supabase.table("sprzet").select("*").eq("id", s_id).execute().data[0]
        
        # Wyświetlamy estetyczną kartę sprzętu
        st.markdown(f"""
        <div class='card'>
            <h3 style='color: #D4AF37; margin-top: 0;'>{dane_sprzetu['nazwa']}</h3>
            <p><b>Numer Seryjny:</b> {dane_sprzetu.get('numer_seryjny') or 'Brak'}</p>
            <p><b>Dostawca:</b> {dane_sprzetu.get('dostawca') or 'Brak'}</p>
            <p><b>Data Zakupu:</b> {dane_sprzetu.get('data_zakupu') or 'Brak'}</p>
            <p><b>Faktura na firmę:</b> {dane_sprzetu.get('na_jaka_firme') or 'Brak'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Wyświetlamy historię napraw
        st.subheader("📜 Historia Napraw i Serwisów")
        historie = supabase.table("serwis").select("*").eq("sprzet_id", s_id).order("data_zgloszenia", desc=True).execute().data
        
        if historie:
            for entry in historie:
                status_color = "#D4AF37" if entry['status_serwisu'] == 'W naprawie' else "#4CAF50"
                with st.expander(f"🔧 {entry['data_zgloszenia']} | {entry['serwis_firma']} | Status: {entry['status_serwisu']}"):
                    st.write(f"**Firma serwisowa:** {entry['serwis_firma']}")
                    st.write(f"**Usterka / Opis:** {entry['rodzaj_naprawy']}")
                    st.write(f"**Data zgłoszenia:** {entry['data_zgloszenia']}")
                    st.write(f"**Data powrotu:** {entry.get('data_powrotu') or 'W trakcie serwisu'}")
                    st.write(f"**Koszt naprawy:** {entry.get('koszt_naprawy') or 0} PLN")
                    st.write(f"**Uwagi:** {entry.get('uwagi_serwisowe') or 'Brak'}")
        else:
            st.info("Ten sprzęt nie posiada jeszcze historii serwisowej.")
