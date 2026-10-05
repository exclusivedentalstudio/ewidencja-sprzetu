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

# --- INICJALIZACJA SUPABASE ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Błąd połączenia z bazą danych: {e}")
    st.stop()

# --- SYSTEM LOGOWANIA ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = res.user.email
            st.success("Zalogowano pomyślnie!")
            st.rerun()
    except Exception as e:
        st.error(f"Błąd logowania: Niepoprawny e-mail lub hasło ({e})")

def logout_user():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = ""
    st.rerun()

# --- EKRAN LOGOWANIA ---
if not st.session_state["logged_in"]:
    st.title("🦷 Exclusive Dental Studio")
    st.subheader("System Ewidencji Sprzętu – Logowanie")
    
    with st.form("login_form"):
        email = st.text_input("Adres e-mail")
        password = st.text_input("Hasło", type="password")
        submit_button = st.form_submit_button("Zaloguj się")
        
        if submit_button:
            if email and password:
                login_user(email, password)
            else:
                st.warning("Uzupełnij e-mail oraz hasło.")
    st.stop()

# --- GŁÓWNY PANEL APLIKACJI (PO ZALOGOWANIU) ---
st.sidebar.write(f"👤 Zalogowano jako: **{st.session_state['user_email']}**")
if st.sidebar.button("Wyloguj się"):
    logout_user()

st.title("🦷 Exclusive Dental Studio – Ewidencja Sprzętu")

# Pobieranie danych o sprzęcie
try:
    res_sprzet = supabase.table("sprzet").select("*").execute()
    data_sprzet = res_sprzet.data
except Exception as e:
    st.error(f"Błąd pobierania danych ze sprzętem: {e}")
    data_sprzet = []

df_sprzet = pd.DataFrame(data_sprzet) if data_sprzet else pd.DataFrame()

tab1, tab2 = st.tabs(["📋 Lista sprzętu", "➕ Dodaj nowy sprzęt"])

# --- ZAKŁADKA 1: LISTA SPRZĘTU ---
with tab1:
    if not df_sprzet.empty:
        st.subheader("Wyszukiwanie i filtrowanie")
        col_szukaj, col_status = st.columns([2, 1])
        
        with col_szukaj:
            szukaj = st.text_input("🔍 Szukaj po nazwie lub numerze seryjnym")
        with col_status:
            statusty = ["Wszystkie"] + list(df_sprzet["status"].dropna().unique()) if "status" in df_sprzet.columns else ["Wszystkie"]
            wybrany_status = st.selectbox("Status", statusty)
        
        df_filtrowane = df_sprzet.copy()
        
        if szukaj:
            mask = (
                df_filtrowane["nazwa"].astype(str).str.contains(szukaj, case=False, na=False) |
                df_filtrowane["numer_seryjny"].astype(str).str.contains(szukaj, case=False, na=False)
            )
            df_filtrowane = df_filtrowane[mask]
            
        if wybrany_status != "Wszystkie" and "status" in df_filtrowane.columns:
            df_filtrowane = df_filtrowane[df_filtrowane["status"] == wybrany_status]

        st.markdown(f"Znaleziono pozycji: **{len(df_filtrowane)}**")
        st.dataframe(df_filtrowane, use_container_width=True)
    else:
        st.info("Baza danych sprzętu jest pusta lub wystąpił problem z wczytaniem.")

# --- ZAKŁADKA 2: DODAWANIE SPRZĘTU ---
with tab2:
    st.subheader("Formularz dodawania nowego urządzenia")
    with st.form("form_nowy_sprzet"):
        col1, col2 = st.columns(2)
        with col1:
            nazwa = st.text_input("Nazwa urządzenia *")
            kategoria = st.text_input("Kategoria")
            numer_seryjny = st.text_input("Numer seryjny")
            dostawca = st.text_input("Dostawca / Serwisant")
        with col2:
            gabinet = st.text_input("Gabinet / Lokalizacja")
            status = st.selectbox("Status", ["Sprawny", "W serwisie", "Wypożyczony", "Zutylizowany"])
            data_przegladu = st.date_input("Data następnego przeglądu", value=None)
            uwagi = st.text_area("Uwagi")

        submit_nowy = st.form_submit_button("Zapisz urządzenie w bazie")
        
        if submit_nowy:
            if nazwa:
                payload = {
                    "nazwa": nazwa,
                    "kategoria": kategoria,
                    "numer_seryjny": numer_seryjny,
                    "status": status,
                    "uwagi": uwagi,
                    "dostawca": dostawca
                }
                if data_przegladu:
                    payload["data_przegladu"] = str(data_przegladu)
                
                try:
                    supabase.table("sprzet").insert(payload).execute()
                    st.success(f"Pomyślnie dodano urządzenie: {nazwa}")
                    st.rerun()
                except Exception as err:
                    st.error(f"Błąd zapisu do bazy: {err}")
            else:
                st.warning("Wypełnij wymagane pole: Nazwa urządzenia.")
