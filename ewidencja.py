import streamlit as st
from supabase import create_client, Client
import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="Exclusive Dental Studio – Zasoby",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Wstrzyknięcie czcionki Google Fonts (Outfit) oraz dopasowanie stylistyki
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&display=swap');

    /* Ukrycie paska Streamlit u góry */
    header[data-testid="stHeader"] {
        background-color: #000000 !important;
        display: none;
    }
    footer {
        visibility: hidden;
    }
    
    /* Główne tło i czcionka dla całej aplikacji */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
        background-color: #000000 !important;
        color: #ffffff;
    }

    [data-testid="stSidebar"] {
        background-color: #080808 !important;
        border-right: 1px solid #1c1c1c;
    }

    /* Nagłówki - bardzo smukła linia i charakterystyczny złoty akcent */
    h1 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 300 !important;
        color: #ffffff !important;
        letter-spacing: 0.5px;
        font-size: 2.2rem !important;
        margin-bottom: 0.2rem;
    }

    .gold-text {
        color: #c5a880 !important;
        font-weight: 600 !important;
    }

    h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 400 !important;
        color: #c5a880 !important;
        letter-spacing: 0.5px;
    }

    p, label, span, div {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 300;
        color: #e5e7eb;
    }

    /* Eleganckie przyciski z zaokrągloną czcionką */
    .stButton>button {
        font-family: 'Outfit', sans-serif !important;
        background: #c5a880 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background: #b3966d !important;
    }

    /* Pola formularza */
    div[data-baseweb="input"] input, div[data-baseweb="select"] div, textarea {
        font-family: 'Outfit', sans-serif !important;
        background-color: #111111 !important;
        color: #ffffff !important;
        border-color: #222222 !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Łączenie z Supabase
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
st.sidebar.markdown("<h3 style='color: #c5a880; margin-bottom:0;'>Exclusive Dental Studio</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 0.85rem; color: #888;'>System Zarządzania Zasobami</p>", unsafe_allow_html=True)
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
st.markdown("<h1>Exclusive Dental Studio <span class='gold-text'>— Zasoby i Sprzęt</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #aaa; font-weight: 200;'>Precyzyjne zarządzanie wyposażeniem kliniki. Harmonijny standard opieki.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

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
    st.markdown("<h3>Aktualny wykaz sprzętu w klinice</h3>", unsafe_allow_html=True)
    try:
        response = supabase.table("sprzet").select("*").execute()
        items = response.data
        if items:
            st.dataframe(items, use_container_width=True)
        else:
            st.info("Baza danych jest obecnie pusta. Użyj formularza powyżej, aby dodać pierwsze urządzenie.")
    except Exception as err:
        st.error(f"Błąd wczytywania danych z chmury: {err}")
