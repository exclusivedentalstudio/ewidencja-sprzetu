import streamlit as st
from supabase import create_client, Client
import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="Exclusive Dental Studio – System Zasobów",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Wstrzyknięcie stylów CSS (ciemny motyw, złote akcenty)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&display=swap');

    header[data-testid="stHeader"] {
        background-color: #000000 !important;
        display: none;
    }
    footer {
        visibility: hidden;
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
    }
    .luxury-card p {
        margin: 0;
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
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip()
    raw_key = st.secrets["SUPABASE_KEY"]
    SUPABASE_KEY = "".join(raw_key.split())
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
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
    # Pobieranie istniejącego sprzętu
    existing_items = []
    try:
        res = supabase.table("sprzet").select("*").execute()
        existing_items = res.data or []
    except Exception:
        existing_items = []

    known_nazwy = sorted(list(set([i["nazwa"] for i in existing_items if i.get("nazwa")])))
    known_kategorie = sorted(list(set([i["kategoria"] for i in existing_items if i.get("kategoria")])))
    known_numery = sorted(list(set([i["numer_seryjny"] for i in existing_items if i.get("numer_seryjny")])))
    known_dostawcy = sorted(list(set([i["dostawca"] for i in existing_items if i.get("dostawca")])))
    known_firmy = sorted(list(set([i["na_jaka_firme"] for i in existing_items if i.get("na_jaka_firme")])))

    # --- SEKCJA 1: DODawanie sprzętu ---
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

            opt_dost = ["➕ Dodaj nowego dostawcę..."] + known_dostawcy
            sel_dost = st.selectbox("Wybierz istniejącego dostawcę lub dodaj nowego", opt_dost)
            dostawca = st.text_input("Dostawca / Od kogo kupiono", placeholder="np. Dental Supply") if sel_dost == "➕ Dodaj nowego dostawcę..." else sel_dost

        with col2:
            opt_firma = ["➕ Dodaj nową firmę/podmiot..."] + known_firmy
            sel_firma = st.selectbox("Wybierz firmę (na kogo kupiono) lub dodaj nową", opt_firma)
            na_jaka_firme = st.text_input("Zakupiono na firmę (NIP / Nazwa)", placeholder="np. Exclusive Dental Clinic") if sel_firma == "➕ Dodaj nową firmę/podmiot..." else sel_firma

            default_date_str = datetime.date.today().strftime("%Y-%m-%d")
            default_future_str = (datetime.date.today() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
            
            data_zakupu = st.text_input("Data zakupu (RRRR-MM-DD)", value=default_date_str)
            data_przegladu = st.text_input("Data następnego przeglądu (RRRR-MM-DD)", value=default_future_str)
            status = st.selectbox("Status sprzętu", ["Sprawny", "W serwisie", "Wymaga przeglądu", "Wycofany"])

        uwagi = st.text_area("Uwagi / Opis", height=80)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Zapisz w bazie sprzętu", type="primary"):
            if not nazwa or nazwa.strip() == "":
                st.warning("Nazwa sprzętu jest wymagana.")
            else:
                try:
                    data_to_insert = {
                        "nazwa": nazwa.strip(),
                        "kategoria": kategoria.strip() if kategoria else "",
                        "numer_seryjny": numer_seryjny.strip() if numer_seryjny else "",
                        "dostawca": dostawca.strip() if dostawca else "",
                        "data_zakupu": data_zakupu.strip() if data_zakupu else None,
                        "data_przegladu": data_przegladu.strip() if data_przegladu else None,
                        "na_jaka_firme": na_jaka_firme.strip() if na_jaka_firme else "",
                        "status": status,
                        "uwagi": uwagi.strip() if uwagi else ""
                    }
                    supabase.table("sprzet").insert(data_to_insert).execute()
                    st.success(f"Dodano pomyślnie: **{nazwa}**")
                    st.rerun()
                except Exception as err:
                    st.error(f"Błąd zapisu do bazy: {err}")

    # --- SEKCJA 2: ZARZĄDZANIE SERWISAMI I NAPRAWAMI ---
    with st.expander("🛠️ Wyślij sprzęt do serwisu / Zarządzaj naprawami", expanded=False):
        st.markdown("<h4 style='color: #c5a880; font-weight: 400;'>Nowe zgłoszenie serwisowe</h4>", unsafe_allow_html=True)
        
        if existing_items:
            # Słownik do wyboru sprzętu
            sprzet_options = {f"{item['nazwa']} (SN: {item.get('numer_seryjny', 'brak')}) [Status: {item.get('status')}]": item for item in existing_items}
            selected_label = st.selectbox("Wybierz urządzenie kierowane do naprawy", list(sprzet_options.keys()))
            chosen_item = sprzet_options[selected_label]

            with st.form("service_form"):
                scol1, scol2 = st.columns(2)
                with scol1:
                    data_zgloszenia = st.text_input("Data zgłoszenia / wysyłki (RRRR-MM-DD)", value=datetime.date.today().strftime("%Y-%m-%d"))
                    serwis_firma = st.text_input("Firma serwisowa / Kto przyjął sprzęt", placeholder="np. Serwis Medyczny Sp. z o.o.")
                with scol2:
                    rodzaj_naprawy = st.selectbox("Rodzaj naprawy", ["Gwarancyjna", "Płatna"])
                    uwagi_serwisowe = st.text_area("Opis usterki / Uwagi", height=70)

                submit_service = st.form_submit_button("Wyślij do serwisu (Zmień status na 'W serwisie')", type="primary")
                if submit_service:
                    try:
                        # 1. Dodaj wpis do tabeli serwis
                        service_data = {
                            "sprzet_id": chosen_item["id"],
                            "nazwa_sprzetu": chosen_item["nazwa"],
                            "numer_seryjny": chosen_item.get("numer_seryjny", ""),
                            "data_zgloszenia": data_zgloszenia,
                            "serwis_firma": serwis_firma,
                            "rodzaj_naprawy": rodzaj_naprawy,
                            "status_serwisu": "W naprawie",
                            "uwagi_serwisowe": uwagi_serwisowe
                        }
                        supabase.table("serwis").insert(service_data).execute()

                        # 2. Zaktualizuj status w tabeli głównej sprzętu na "W serwisie"
                        supabase.table("sprzet").update({"status": "W serwisie"}).eq("id", chosen_item["id"]).execute()

                        st.success(f"Urządzenie **{chosen_item['nazwa']}** zostało skierowane do serwisu. Status zmieniony na 'W serwisie'.")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Błąd rejestracji serwisu: {err}")
        else:
            st.info("Brak sprzętu w bazie. Dodaj najpierw urządzenie.")

        st.markdown("<hr style='border-color: #222;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #c5a880; font-weight: 400; margin-top: 20px;'>Aktywne naprawy / Zwrot z serwisu</h4>", unsafe_allow_html=True)
        
        try:
            active_services = supabase.table("serwis").select("*").eq("status_serwisu", "W naprawie").execute().data
            if active_services:
                for s in active_services:
                    with st.container():
                        st.markdown(f"""
                            <div style='background: #141414; padding: 15px; border-radius: 6px; border: 1px solid #2a2a2a; margin-bottom: 10px;'>
                                <strong>{s['nazwa_sprzetu']}</strong> (SN: {s['numer_seryjny']})<br>
                                <span style='color: #aaa;'>Serwis:</span> {s['serwis_firma']} | <span style='color: #aaa;'>Typ:</span> {s['rodzaj_naprawy']} | <span style='color: #aaa;'>Wysłano:</span> {s['data_zgloszenia']}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        with st.form(f"return_form_{s['id']}"):
                            rcol1, rcol2 = st.columns(2)
                            with rcol1:
                                data_powrotu = st.text_input("Data powrotu z serwisu (RRRR-MM-DD)", value=datetime.date.today().strftime("%Y-%m-%d"), key=f"ret_date_{s['id']}")
                            with rcol2:
                                koszt_naprawy = st.number_input("Koszt naprawy (PLN)", min_value=0.0, step=10.0, value=0.0, key=f"cost_{s['id']}")
                            
                            finish_service = st.form_submit_button("Zatwierdź powrót (Zmień status na 'Sprawny')", type="primary")
                            if finish_service:
                                try:
                                    # 1. Zaktualizuj wpis w tabeli serwis
                                    supabase.table("serwis").update({
                                        "status_serwisu": "Zakończony",
                                        "data_powrotu": data_powrotu,
                                        "koszt_naprawy": koszt_naprawy
                                    }).eq("id", s["id"]).execute()

                                    # 2. Zmień status sprzętu z powrotem na "Sprawny"
                                    supabase.table("sprzet").update({"status": "Sprawny"}).eq("id", s["sprzet_id"]).execute()

                                    st.success("Urządzenie pomyślnie wróciło z serwisu i odzyskało status 'Sprawny'!")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Błąd aktualizacji: {err}")
            else:
                st.info("Brak urządzeń aktualnie przebywających w serwisie.")
        except Exception as err:
            st.error(f"Błąd pobierania historii serwisu: {err}")

    # --- SEKCJA 3: WYKAZ SPRZĘTU ---
    st.markdown("<h3 style='color: #c5a880; font-weight: 400; font-size: 1.3rem; margin-top: 30px;'>Aktualny wykaz sprzętu medycznego</h3>", unsafe_allow_html=True)
    try:
        response = supabase.table("sprzet").select("*").execute()
        items = response.data
        if items:
            st.dataframe(items, use_container_width=True)
        else:
            st.info("Baza danych jest obecnie pusta. Użyj formularza powyżej, aby dodać pierwsze urządzenie.")
    except Exception as err:
        st.error(f"Błąd wczytywania danych z chmury: {err}")
