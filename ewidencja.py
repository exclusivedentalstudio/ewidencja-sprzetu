import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client, Client

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Ewidencja Sprzętu - Exclusive Dental Studio",
    page_icon="🦷",
    layout="wide"
)

# --- INICJALIZACJA BAZY DANYCH SUPABASE ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Błąd połączenia z bazą danych Supabase: {e}")
    st.stop()

# --- GŁÓWNY INTERFEJS APLIKACI ---
st.title("🦷 Exclusive Dental Studio – Ewidencja Sprzętu")
st.markdown("Witaj w systemie zarządzania sprzętem i historią serwisową gabinetu.")

# Pobieranie danych ze sprzętu
try:
    response = supabase.table("sprzet").select("*").execute()
    data = response.data
except Exception as e:
    st.error(f"Błąd wczytywania danych z chmury: {e}")
    data = []

if data:
    df = pd.DataFrame(data)
    st.success(f"Pomyślnie wczytano {len(df)} pozycji sprzętu z bazy danych.")
    
    # Wyświetlenie tabeli
    st.dataframe(df, use_container_width=True)
else:
    st.info("Baza danych jest obecnie pusta lub trwa ładowanie.")

# Sekcja dodawania nowego sprzętu
with st.expander("➕ Dodaj nowe urządzenie"):
    with st.form("dodaj_sprzet_form"):
        nazwa = st.text_input("Nazwa urządzenia")
        numer_seryjny = st.text_input("Numer seryjny")
        gabinet = st.text_input("Gabinet / Lokalizacja")
        data_zakupu = st.date_input("Data zakupu", value=date.today())
        
        submitted = st.form_submit_button("Zapisz urządzenie")
        if submitted:
            if nazwa:
                try:
                    supabase.table("sprzet").insert({
                        "nazwa": nazwa,
                        "numer_seryjny": numer_seryjny,
                        "gabinet": gabinet,
                        "data_zakupu": str(data_zakupu)
                    }).execute()
                    st.success("Dodano nowe urządzenie do bazy!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Błąd podczas zapisu: {err}")
            else:
                st.warning("Nazwa urządzenia jest wymagana.")
