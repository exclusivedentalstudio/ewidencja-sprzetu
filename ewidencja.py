import streamlit as st
from supabase import create_client, Client
import datetime

# Ustawienia strony Streamlit
st.set_page_config(page_title="Ewidencja Sprzętu Medycznego", page_icon="🏥", layout="wide")

# Pobieranie i czyszczenie sekretów (usuwanie złamań linii z klucza)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip()
    raw_key = st.secrets["SUPABASE_KEY"]
    # Usuwamy wszystkie znaki nowej linii i białe znaki, które mogły powstać przy wklejaniu
    SUPABASE_KEY = "".join(raw_key.split())
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Błąd konfiguracji Supabase w Secrets: {e}")
    st.stop()

# Inicjalizacja stanu sesji dla zalogowanego użytkownika
if "user" not in st.session_state:
    st.session_state["user"] = None

# Sidebar - Logowanie i Rejestracja
st.sidebar.title("🔐 Autoryzacja")

if st.session_state["user"] is None:
    tab_login, tab_register = st.sidebar.tabs(["Zaloguj się", "Zarejestruj się"])
    
    with tab_login:
        email = st.text_input("E-mail", key="login_email")
        password = st.text_input("Hasło", type="password", key="login_password")
        if st.button("Zaloguj", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = res.user
                st.success("Zalogowano pomyślnie!")
                st.rerun()
            except Exception as err:
                st.error(f"Błąd logowania: {err}")
                
    with tab_register:
        reg_email = st.text_input("E-mail do rejestracji", key="reg_email")
        reg_password = st.text_input("Hasło (min. 6 znaków)", type="password", key="reg_password")
        if st.button("Załóż konto", use_container_width=True):
            try:
                res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                st.success("Konto zostało utworzone! Możesz się teraz zalogować.")
            except Exception as err:
                st.error(f"Błąd rejestracji: {err}")
else:
    user_email = st.session_state["user"].email
    st.sidebar.write(f"Zalogowano jako: **{user_email}**")
    if st.sidebar.button("Wyloguj się", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state["user"] = None
        st.rerun()

# Główna część aplikacji
st.title("🏥 Ewidencja Sprzętu Medycznego")

if st.session_state["user"] is None:
    st.info("🔒 Dostęp do systemu wymaga zalogowania. Skorzystaj z panelu bocznego, aby się zalogować lub założyć konto.")
else:
    # Sekcja dodawania nowego sprzętu
    with st.expander("➕ Dodaj nowy sprzęt"):
        with st.form("add_equipment_form", clear_on_submit=True):
            nazwa = st.text_input("Nazwa sprzętu*")
            kategoria = st.text_input("Kategoria")
            numer_seryjny = st.text_input("Numer seryjny")
            data_przegladu = st.date_input("Data następnego przeglądu", value=datetime.date.today())
            status = st.selectbox("Status", ["Sprawny", "W serwisie", "Wymaga przeglądu", "Wycofany"])
            uwagi = st.text_area("Uwagi")
            
            submitted = st.form_submit_button("Zapisz sprzęt w bazie")
            if submitted:
                if not nazwa:
                    st.warning("Nazwa sprzętu jest wymagana!")
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
                        st.success(f"Dodano sprzęt: {nazwa}")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Błąd zapisu do bazy: {err}")

    st.subheader("📋 Baza sprzętu medycznego")
    try:
        response = supabase.table("sprzet").select("*").execute()
        items = response.data
        if items:
            st.dataframe(items, use_container_width=True)
        else:
            st.info("Baza danych jest obecnie pusta. Dodaj pierwszy sprzęt powyżej.")
    except Exception as err:
        st.error(f"Błąd wczytywania danych z chmury: {err}")
