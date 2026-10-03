import streamlit as st
from supabase import create_client, Client
import datetime

# Konfiguracja strony i motywu
st.set_page_config(
    page_title="Exclusive Dental Studio – Zasoby",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nadpisanie stylów CSS – dopasowanie do eleganckiej identyfikacji wizualnej (głębokie cienie, jasna czytelność, złote akcenty premium)
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #ffffff;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    .stButton>button {
        background-color: #c5a880;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #b3966d;
        color: #ffffff;
    }
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        background-color: #161e2d;
        color: #ffffff;
        border-color: #2d3748;
    }
    </style>
""", unsafe_allow_html=True)

# Łączenie z Supabase i czyszczenie sekretów
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip()
    raw_key = st.secrets["SUPABASE_KEY"]
    SUPABASE_KEY = "".join(raw_key.split())
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Błąd konfiguracji Supabase: {e}")
    st.stop()

# Lista adresów e-mail z uprawnieniami Administratora
ADMIN_EMAILS = ["exclusivedentalstudio@gmail.com"]

# Stan sesji
if "user" not in st.session_state:
    st.session_state["user"] = None

# --- PANEL BOCZNY (Autoryzacja) ---
st.sidebar.markdown("### 🦷 Exclusive Dental Studio")
st.sidebar.markdown("---")

if st.session_state["user"] is None:
    tab_login, tab_register = st.sidebar.tabs(["Zaloguj się", "Zarejestruj się"])
    
    with tab_login:
        email = st.text_input("Adres e-mail", key="login_email")
        password = st.text_input("Hasło", type="password", key="login_password")
        if st.button("Zaloguj do systemu", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = res.user
                st.success("Zalogowano pomyślnie!")
                st.rerun()
            except Exception as err:
                st.error(f"Błąd logowania: {err}")
                
    with tab_register:
        reg_email = st.text_input("Adres e-mail", key="reg_email")
        reg_password = st.text_input("Hasło (min. 6 znaków)", type="password", key="reg_password")
        if st.button("Utwórz nowe konto", use_container_width=True):
            try:
                res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                st.success("Konto utworzone! Możesz się teraz zalogować.")
            except Exception as err:
                st.error(f"Błąd rejestracji: {err}")
else:
    user_email = st.session_state["user"].email
    is_admin = user_email.lower() in [e.lower() for e in ADMIN_EMAILS]
    
    st.sidebar.markdown(f"**Użytkownik:**\n`{user_email}`")
    if is_admin:
        st.sidebar.markdown("👑 **Rola:** Administrator")
    else:
        st.sidebar.markdown("👤 **Rola:** Użytkownik")
        
    st.sidebar.markdown("---")
    if st.sidebar.button("Wyloguj się", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state["user"] = None
        st.rerun()

# --- GŁÓWNA CZĘŚĆ APLIKACJI ---
st.title("✨ Exclusive Dental Studio — Zasoby i Sprzęt Medyczny")
st.markdown("Precyzyjne zarządzanie wyposażeniem kliniki. Harmonijny standard opieki.")

if st.session_state["user"] is None:
    st.info("🔒 Dostęp do systemu wymaga autoryzacji. Proszę zalogować się za pomocą panelu bocznego.")
else:
    user_email = st.session_state["user"].email
    is_admin = user_email.lower() in [e.lower() for e in ADMIN_EMAILS]

    # Sekcja dodawania sprzętu
    with st.expander("➕ Dodaj nowy element do bazy sprzętu", expanded=False):
        with st.form("add_equipment_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nazwa = st.text_input("Nazwa sprzętu *")
                kategoria = st.text_input("Kategoria (np. Chirurgia, Diagnostyka)")
                numer_seryjny = st.text_input("Numer seryjny / ID")
            with col2:
                data_przegladu = st.date_input("Data następnego przeglądu", value=datetime.date.today())
                status = st.selectbox("Status", ["Sprawny", "W serwisie", "Wymaga przeglądu", "Wycofany"])
                uwagi = st.text_area("Uwagi / Opis", height=68)
            
            submitted = st.form_submit_button("Zapisz w bazie", type="primary")
            if submitted:
                if not nazwa:
                    st.warning("Nazwa sprzętu jest wymagana.")
                else:
                    try:
                        data_to_insert = {
                            "nazwa": nazwa,
                            "kategoria": kategoria,
                            "numer_seryjny": numer_seryjny,
                            "data_przegladu": str(data_przegladu),
                            "status": status,
                            "uwagi": uwagi
                        }
                        supabase.table("sprzet").insert(data_to_insert).execute()
                        st.success(f"Dodano pomyślnie: **{nazwa}**")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Błąd zapisu do bazy: {err}")

    # Wyświetlanie bazy sprzętu
    st.markdown("### 📋 Aktualny wykaz sprzętu w klinice")
    try:
        response = supabase.table("sprzet").select("*").execute()
        items = response.data
        if items:
            st.dataframe(items, use_container_width=True)
        else:
            st.info("Baza danych jest obecnie pusta. Użyj formularza powyżej, aby dodać pierwsze urządzenie.")
    except Exception as err:
        st.error(f"Błąd wczytywania danych z chmury: {err}")
