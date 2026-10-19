import streamlit as st
from supabase import create_client, Client
import datetime

st.set_page_config(
    page_title="Exclusive Dental Studio – System Zasobów",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bezpieczny CSS (jednoliniowy string, nie wygeneruje błędu cudzysłowu)
st.markdown("<style>@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&display=swap'); header[data-testid='stHeader'], [data-testid='stToolbar'], [data-testid='stStatusWidget'], #MainMenu, footer {display: none !important;} html, body, [class*='css'], .stApp {font-family: 'Outfit', sans-serif !important; background-color: #000000 !important; color: #ffffff;} [data-testid='stSidebar'] {background-color: #050505 !important; border-right: 1px solid #1a1a1a;} .brand-title {font-family: 'Outfit', sans-serif !important; font-weight: 300 !important; font-size: 2.2rem !important; color: #ffffff !important;} .gold-accent {color: #c5a880 !important; font-weight: 600 !important;} .brand-subtitle {font-family: 'Outfit', sans-serif !important; font-weight: 200 !important; font-size: 1.05rem !important; color: #aaaaaa !important;} .luxury-card {background-color: #0d0d0d; border: 1px solid #1f1f1f; border-left: 3px solid #c5a880; padding: 24px; border-radius: 6px; margin: 15px 0;} .stExpander {background-color: #0d0d0d !important; border: 1px solid #222222 !important; border-radius: 6px !important;} div[data-baseweb='input'] input, div[data-baseweb='select'] div, textarea {font-family: 'Outfit', sans-serif !important; background-color: #141414 !important; color: #ffffff !important; border: 1px solid #2a2a2a !important;} .stButton>button {font-family: 'Outfit', sans-serif !important; background: #c5a880 !important; color: #000000 !important; border: none !important; border-radius: 4px !important; font-weight: 600 !important; text-transform: uppercase; font-size: 0.85rem !important; padding: 10px 16px !important;}</style>", unsafe_allow_html=True)

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

# --- PANEL BOCZNY ---
st.sidebar.markdown("<div style='padding-top: 10px;'><div style='font-size: 0.75rem; color: #c5a880; font-weight: 600;'>Klinika Stomatologiczna</div><div style='font-size: 1.25rem; font-weight: 300; color: #ffffff;'>Exclusive Dental Studio</div></div>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color: #1a1a1a; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

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
                st.success("Konto utworzone! Możesz się zalogować.")
            except Exception as err:
                st.error(f"Błąd rejestracji: {err}")
else:
    user_email = st.session_state["user"].email
    is_admin = user_email.lower() in [e.lower() for e in ADMIN_EMAILS]
    st.sidebar.markdown(f"<div style='font-size:0.9rem; color:#888;'>Zalogowany jako:</div><div style='font-size:0.95rem; color:#fff;'>{user_email}</div>", unsafe_allow_html=True)
    if is_admin:
        st.sidebar.markdown("<span style='background:#1f1911; color:#c5a880; border:1px solid #3d3120; padding:4px 10px; border-radius:4px; font-size:0.8rem;'>👑 Administrator</span>", unsafe_allow_html=True)
    if st.sidebar.button("Wyloguj się", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state["user"] = None
        st.rerun()

# --- GŁÓWNA APLIKACJA ---
col_head, col_logo = st.columns([4, 1])
with col_head:
    st.markdown("<div class='brand-title'>System Zarządzania <span class='gold-accent'>Zasobami i Sprzętem</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>Precyzyjna kontrola wyposażenia kliniki. Harmonia i pełen komfort pracy.</div>", unsafe_allow_html=True)

if st.session_state["user"] is not None:
    existing_items = []
    try:
        res = supabase.table("sprzet").select("*").order("id", desc=False).execute()
        existing_items = res.data or []
    except Exception:
        existing_items = []

    # --- TABELA GŁÓWNA ---
    st.markdown("<h3 style='color: #c5a880; font-weight: 400; font-size: 1.3rem; margin-top: 20px;'>Aktualny wykaz sprzętu medycznego</h3>", unsafe_allow_html=True)
    
    if existing_items:
        display_list = []
        for idx, item in enumerate(existing_items, 1):
            gwarancja_txt = "Tak" if item.get("czy_gwarancja") else "Nie"
            row = {
                "Lp.": idx,
                "nazwa": item.get("nazwa") or "—",
                "kategoria": item.get("kategoria") or "—",
                "numer_seryjny": item.get("numer_seryjny") or "—",
                "lokalizacja": item.get("lokalizacja") or "—",
                "status": item.get("status") or "—",
                "data_przegladu": item.get("data_przegladu") or "—",
                "uwagi": item.get("uwagi") or "—",
                "gwarancja": gwarancja_txt
            }
            display_list.append(row)

        st.dataframe(display_list, use_container_width=True)

        st.markdown("<h4 style='color: #c5a880; font-weight: 400; margin-top: 25px;'>📋 Wybierz sprzęt z listy do szczegółowego podglądu</h4>", unsafe_allow_html=True)
        item_map = {f"{i['nazwa']} | SN: {i.get('numer_seryjny', 'Brak')}": i for i in existing_items}
        selected_item_label = st.selectbox("Wybierz urządzenie:", ["-- Wybierz urządzenie --"] + list(item_map.keys()))
        
        if selected_item_label != "-- Wybierz urządzenie --":
            chosen_device = item_map[selected_item_label]
            dev_id = chosen_device["id"]
            
            st.markdown(f"""
            <div class='luxury-card'>
                <h2 style='color: #c5a880; margin-top: 0;'>{chosen_device['nazwa']}</h2>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                    <p><b>Kategoria:</b> {chosen_device.get('kategoria') or '—'}</p>
                    <p><b>Numer Seryjny:</b> {chosen_device.get('numer_seryjny') or '—'}</p>
                    <p><b>Lokalizacja:</b> {chosen_device.get('lokalizacja') or '—'}</p>
                    <p><b>Dostawca:</b> {chosen_device.get('dostawca') or '—'}</p>
                    <p><b>Zakupiono na firmę:</b> {chosen_device.get('na_jaka_firme') or '—'}</p>
                    <p><b>Data Zakupu:</b> {chosen_device.get('data_zakupu') or '—'}</p>
                    <p><b>Przegląd do:</b> {chosen_device.get('data_przegladu') or '—'}</p>
                    <p><b>Status:</b> {chosen_device.get('status') or '—'}</p>
                </div>
                <p style='margin-top: 10px;'><b>Uwagi:</b> {chosen_device.get('uwagi') or 'Brak'}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🗑️ Usuń ten sprzęt", key=f"del_{dev_id}"):
                supabase.table("serwis").delete().eq("sprzet_id", dev_id).execute()
                supabase.table("sprzet").delete().eq("id", dev_id).execute()
                st.success("Sprzęt usunięty.")
                st.rerun()
    else:
        st.info("Baza sprzętu jest pusta.")
