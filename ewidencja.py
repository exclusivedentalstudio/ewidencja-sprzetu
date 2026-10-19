import streamlit as st
from supabase import create_client, Client
import datetime

# Konfiguracja strony - otwarty sidebar domyślnie
st.set_page_config(
    page_title="Exclusive Dental Studio – System Zasobów",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stylizacja CSS - ukrycie nagłówka, paska Streamlit i dolnych plakietek
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&display=swap');

    /* Ukrycie górnego paska nagłówka Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Ukrycie paska "Hosted with Streamlit" oraz zielonej ikonki na dole po prawej */
    [data-testid="stStatusWidget"],
    #MainMenu,
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    div[class*="viewerBadge"],
    div[class*="stAppDeployButton"],
    footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Podświetlenie ikony/przycisku otwierania panelu bocznego */
    button[data-testid="stHeaderSidebarButton"] {
        color: #c5a880 !important;
        background-color: #111111 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 4px !important;
    }
    button[data-testid="stHeaderSidebarButton"]:hover {
        border-color: #c5a880 !important;
        color: #ffffff !important;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
        background-color: #000000 !important;
        color: #ffffff;
    }

    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #1a1a1a;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 300 !important;
        color: #888888 !important;
        background-color: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #c5a880 !important;
        font-weight: 500 !important;
        border-bottom: 2px solid #c5a880 !important;
    }

    .brand-title {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 300 !important;
        font-size: 2.2rem !important;
        color: #ffffff !important;
        letter-spacing: 0.5px;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .gold-accent {
        color: #c5a880 !important;
        font-weight: 600 !important;
    }
    .brand-subtitle {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 200 !important;
        font-size: 1.05rem !important;
        color: #aaaaaa !important;
        margin-top: 6px;
        margin-bottom: 25px;
    }

    .luxury-card {
        background-color: #0d0d0d;
        border: 1px solid #1f1f1f;
        border-left: 3px solid #c5a880;
        padding: 24px;
        border-radius: 6px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .luxury-card p {
        margin: 6px 0;
        font-weight: 300;
        color: #d1d5db;
        font-size: 1rem;
    }

    .stExpander {
        background-color: #0d0d0d !important;
        border: 1px solid #222222 !important;
        border-radius: 6px !important;
    }
    .stExpander details {
        background-color: #0d0d0d !important;
        color: #ffffff !important;
    }
    .stExpander summary {
        background-color: #121212 !important;
        color: #c5a880 !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
    }
    .stExpander summary:hover {
        color: #ffffff !important;
        background-color: #1a1a1a !important;
    }
    .stExpander [data-testid="stExpanderDetails"] {
        background-color: #0d0d0d !important;
        padding: 20px !important;
    }

    label, div[data-testid="stMarkdownContainer"] p {
        color: #cccccc !important;
    }

    div[data-baseweb="input"] input, div[data-baseweb="select"] div, textarea {
        font-family: 'Outfit', sans-serif !important;
        background-color: #141414 !important;
        color: #ffffff !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 4px !important;
    }
    div[data-baseweb="input"] input:focus, textarea:focus {
        border-color: #c5a880 !important;
    }

    .stButton>button {
        font-family: 'Outfit', sans-serif !important;
        background: #c5a880 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        font-size: 0.85rem !important;
        padding: 10px 16px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background: #d1b58d !important;
        color: #000000 !important;
        box-shadow: 0 4px 15px rgba(197, 168, 128, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Połączenie z Supabase
@st.cache_resource
def init_supabase() -> Client:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip()
    raw_key = st.secrets["SUPABASE_KEY"]
    SUPABASE_KEY = "".join(raw_key.split())
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Błąd konfiguracji Supabase: {e}")
    st.stop()

ADMIN_EMAILS = ["exclusivedentalstudio@gmail.com"]

if "user" not in st.session_state:
    st.session_state["user"] = None

# --- PANEL BOCZNY (Autoryzacja) ---
st.sidebar.markdown("""
    <div style='padding-top: 10px; padding-bottom: 5px;'>
        <div style='font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; color: #c5a880; font-weight: 600;'>Klinika Stomatologiczna</div>
        <div style='font-size: 1.25rem; font-weight: 300; color: #ffffff; letter-spacing: 0.5px;'>Exclusive Dental Studio</div>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color: #1a1a1a; margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

if st.session_state["user"] is None:
    tab_login, tab_register = st.sidebar.tabs(["Zaloguj się", "Zarejestruj się"])
    
    with tab_login:
        email = st.text_input("Adres e-mail", key="login_email")
        password = st.text_input("Hasło", type="password", key="login_password")
        st.markdown("<br>", unsafe_allow_html=True)
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
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Utwórz nowe konto", use_container_width=True):
            try:
                res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                st.success("Konto utworzone! Możesz się teraz zalogować.")
            except Exception as err:
                st.error(f"Błąd rejestracji: {err}")
else:
    user_email = st.session_state["user"].email
    is_admin = user_email.lower() in [e.lower() for e in ADMIN_EMAILS]
    
    st.sidebar.markdown(f"<div style='font-size:0.9rem; color:#888;'>Zalogowany jako:</div><div style='font-size:0.95rem; color:#fff; font-weight:500;'>{user_email}</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if is_admin:
        st.sidebar.markdown("<span style='background:#1f1911; color:#c5a880; border:1px solid #3d3120; padding:4px 10px; border-radius:4px; font-size:0.8rem; font-weight:500;'>👑 Administrator</span>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<span style='background:#111111; color:#aaaaaa; border:1px solid #222222; padding:4px 10px; border-radius:4px; font-size:0.8rem; font-weight:500;'>👤 Użytkownik</span>", unsafe_allow_html=True)
        
    st.sidebar.markdown("<hr style='border-color: #1a1a1a; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    if st.sidebar.button("Wyloguj się", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state["user"] = None
        st.rerun()

# --- GŁÓWNA CZĘŚĆ APLIKACJI ---
col_head, col_logo = st.columns([4, 1])
with col_head:
    st.markdown("<div class='brand-title'>System Zarządzania <span class='gold-accent'>Zasobami i Sprzętem</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>Precyzyjna kontrola wyposażenia kliniki. Harmonia i pełen komfort pracy.</div>", unsafe_allow_html=True)

with col_logo:
    st.markdown("""
        <div style='text-align: right; padding-top: 5px;'>
            <span style='border: 1px solid #c5a880; color: #c5a880; padding: 8px 16px; font-size: 0.8rem; letter-spacing: 2px; font-weight: 500; border-radius: 2px;'>EDS SYSTEM</span>
        </div>
    """, unsafe_allow_html=True)

if st.session_state["user"] is None:
    st.markdown("""
        <div class='luxury-card'>
            <p>🔒 <strong>Dostęp zastrzeżony.</strong> Aby uzyskać dostęp do ewidencji i bazy sprzętu medycznego Exclusive Dental Studio, zaloguj się lub zarejestruj konto w panelu bocznym.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    existing_items = []
    try:
        res = supabase.table("sprzet").select("*").order("id", desc=False).execute()
        existing_items = res.data or []
    except Exception:
        existing_items = []

    known_nazwy = sorted(list(set([i["nazwa"] for i in existing_items if i.get("nazwa")])))
    known_kategorie = sorted(list(set([i["kategoria"] for i in existing_items if i.get("kategoria")])))
    known_numery = sorted(list(set([i["numer_seryjny"] for i in existing_items if i.get("numer_seryjny")])))
    known_dostawcy = sorted(list(set([i["dostawca"] for i in existing_items if i.get("dostawca")])))
    known_firmy = sorted(list(set([i["na_jaka_firme"] for i in existing_items if i.get("na_jaka_firme")])))
    known_lokalizacje = sorted(list(set([i["lokalizacja"] for i in existing_items if i.get("lokalizacja")])))

    # --- SEKCJA 1: DODAWANIE SPRZĘTU ---
    with st.expander("➕ Dodaj nowy element do bazy sprzętu", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            opt_nazwa = ["➕ Dodaj nową nazwę..."] + known_nazwy
            sel_nazwa = st.selectbox("Wybierz istniejącą nazwę sprzętu lub dodaj nową", opt_nazwa)
            nazwa = st.text_input("Nazwa sprzętu *", placeholder="np. Mikroskop Stomatologiczny") if sel_nazwa == "➕ Dodaj nową nazwę..." else sel_nazwa

            opt_kat = ["➕ Dodaj nową kategorię..."] + known_kategorie
            sel_kat = st.selectbox("Wybierz istniejącą kategorię lub dodaj nową", opt_kat)
            kategoria = st.text_input("Kategoria", placeholder="np. Endodoncja") if sel_kat == "➕ Dodaj nową kategorię..." else sel_kat

            opt_sn = ["➕ Wpisz nowy numer seryjny..."] + known_numery
            sel_sn = st.selectbox("Wybierz istniejący numer seryjny lub dodaj nowy", opt_sn)
            numer_seryjny = st.text_input("Numer seryjny / ID", placeholder="np. SN-2024-889") if sel_sn == "➕ Wpisz nowy numer seryjny..." else sel_sn

            opt_lokalizacja = ["➕ Wpisz nową lokalizację..."] + known_lokalizacje
            sel_lokalizacja = st.selectbox("Wybierz lokalizację lub wpisz nową", opt_lokalizacja)
            lokalizacja = st.text_input("Gdzie się znajduje / Lokalizacja", placeholder="np. Gabinet 1 / Sterylizatornia / Magazyn") if sel_lokalizacja == "➕ Wpisz nową lokalizację..." else sel_lokalizacja

        with col2:
            opt_dost = ["➕ Dodaj nowego dostawcę..."] + known_dostawcy
            sel_dost = st.selectbox("Wybierz istniejącego dostawcę lub dodaj nowego", opt_dost)
            dostawca = st.text_input("Dostawca / Od kogo kupiono", placeholder="np. Dental Supply") if sel_dost == "➕ Dodaj nowego dostawcę..." else sel_dost

            opt_firma = ["➕ Dodaj nową firmę/podmiot..."] + known_firmy
            sel_firma = st.selectbox("Wybierz firmę (na kogo kupiono) lub dodaj nową", opt_firma)
            na_jaka_firme = st.text_input("Zakupiono na firmę (NIP / Nazwa)", placeholder="np. Exclusive Dental Clinic") if sel_firma == "➕ Dodaj nową firmę/podmiot..." else sel_firma

            default_date_str = datetime.date.today().strftime("%Y-%m-%d")
            default_future_str = (datetime.date.today() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
            default_guarantee_str = (datetime.date.today() + datetime.timedelta(days=730)).strftime("%Y-%m-%d")
            
            data_zakupu = st.text_input("Data zakupu (RRRR-MM-DD)", value=default_date_str)
            data_przegladu = st.text_input("Data następnego przeglądu (RRRR-MM-DD)", value=default_future_str)
            
            czy_gwarancja = st.checkbox("Sprzęt objęty gwarancją", value=True)
            gwarancja_do = ""
            if czy_gwarancja:
                gwarancja_do = st.text_input("Gwarancja ważna do (RR
