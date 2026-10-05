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

# --- GŁÓWNY PANEL APLIKACJI ---
st.sidebar.write(f"👤 Zalogowano jako: **{st.session_state['user_email']}**")
if st.sidebar.button("Wyloguj się"):
    logout_user()

st.title("🦷 Exclusive Dental Studio – Ewidencja Sprzętu")

# Pobieranie danych
try:
    res_sprzet = supabase.table("sprzet").select("*").execute()
    data_sprzet = res_sprzet.data
except Exception as e:
    st.error(f"Błąd pobierania sprzętu: {e}")
    data_sprzet = []

try:
    res_serwis = supabase.table("serwis").select("*").execute()
    data_serwis = res_serwis.data
except Exception as e:
    data_serwis = []

df_sprzet = pd.DataFrame(data_sprzet) if data_sprzet else pd.DataFrame()

tab1, tab2, tab3 = st.tabs(["📋 Lista sprzętu", "🛠️ Zgłoszenia serwisowe", "➕ Dodaj nowy sprzęt"])

# --- ZAKŁADKA 1: LISTA SPRZĘTU ---
with tab1:
    if not df_sprzet.empty:
        st.subheader("Wyszukiwanie i filtrowanie sprzętu")
        col_szukaj, col_status = st.columns([2, 1])
        
        with col_szukaj:
            szukaj = st.text_input("🔍 Szukaj po nazwie lub numerze seryjnym")
        with col_status:
            statusty = ["Wszystkie"] + list(df_sprzet["status"].dropna().unique()) if "status" in df_sprzet.columns else ["Wszystkie"]
            wybrany_status = st.selectbox("Status sprzętu", statusty)
        
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
        st.info("Baza danych sprzętu jest pusta lub trwa ładowanie.")

# --- ZAKŁADKA 2: ZGŁOSZENIA SERWISOWE (EDYCJA I USUWANIE) ---
with tab2:
    st.subheader("Zarządzanie zgłoszeniami serwisowymi")

    # Formularz dodawania nowego zgłoszenia
    with st.expander("➕ Dodaj nowe zgłoszenie serwisowe"):
        if not df_sprzet.empty:
            with st.form("form_nowe_zgloszenie"):
                opcje_sprzetu = {f"{row['nazwa']} (SN: {row.get('numer_seryjny', 'brak')})": row['id'] for _, row in df_sprzet.iterrows()}
                wybrane_urzadzenie_label = st.selectbox("Wybierz urządzenie", list(opcje_sprzetu.keys()))
                
                opis_zgloszenia = st.text_area("Opis usterki / zgłoszenia *")
                data_zgloszenia = st.date_input("Data zgłoszenia", value=date.today())
                koszt = st.number_input("Szacowany / Rzeczywisty koszt (zł)", min_value=0.0, step=10.0)
                status_serwisu = st.selectbox("Status zgłoszenia", ["Zgłoszone", "W trakcie naprawy", "Zakończone", "Anulowane"])
                
                submit_zgloszenie = st.form_submit_button("Zapisz zgłoszenie serwisowe")
                
                if submit_zgloszenie:
                    if opis_zgloszenia:
                        id_sprzetu = opcje_sprzetu[wybrane_urzadzenie_label]
                        payload_serwis = {
                            "sprzet_id": id_sprzetu,
                            "opis": opis_zgloszenia,
                            "data_zgloszenia": str(data_zgloszenia),
                            "koszt": koszt,
                            "status": status_serwisu
                        }
                        try:
                            supabase.table("serwis").insert(payload_serwis).execute()
                            st.success("Dodano nowe zgłoszenie serwisowe!")
                            st.rerun()
                        except Exception as err:
                            st.error(f"Błąd zapisu zgłoszenia: {err}")
                    else:
                        st.warning("Uzupełnij opis zgłoszenia.")
        else:
            st.warning("Najpierw dodaj sprzęt w bazie, aby móc rejestrować zgłoszenia serwisowe.")

    st.divider()
    st.write("### Lista zgłoszeń w bazie")

    if data_serwis:
        for zgl in data_serwis:
            zgl_id = zgl.get("id")
            sprzet_id = zgl.get("sprzet_id")
            
            # Pobranie nazwy sprzętu na podstawie ID
            nazwa_sprzetu = "Nieokreślony sprzęt"
            if not df_sprzet.empty and "id" in df_sprzet.columns:
                pasujacy_sprzet = df_sprzet[df_sprzet["id"] == sprzet_id]
                if not pasujacy_sprzet.empty:
                    nazwa_sprzetu = pasujacy_sprzet.iloc[0]["nazwa"]

            with st.container():
                col_info, col_akcje = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"**🛠️ Sprzęt:** {nazwa_sprzetu}")
                    st.markdown(f"**Data:** {zgl.get('data_zgloszenia', 'Brak')} | **Status:** `{zgl.get('status', 'Nieokreślony')}` | **Koszt:** {zgl.get('koszt', 0)} zł")
                    st.markdown(f"**Opis:** {zgl.get('opis', 'Brak opisu')}")

                with col_akcje:
                    # Przycisk usuwania
                    if st.button("🗑️ Usuń", key=f"del_serwis_{zgl_id}"):
                        try:
                            supabase.table("serwis").delete().eq("id", zgl_id).execute()
                            st.success("Zgłoszenie zostało usunięte!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd podczas usuwania: {e}")

                # Sekcja edycji w rozwijanym panelu
                with st.expander(f"✏️ Edytuj zgłoszenie (ID: {zgl_id})"):
                    with st.form(f"form_edytuj_serwis_{zgl_id}"):
                        nowy_opis = st.text_area("Opis usterki", value=zgl.get("opis", ""))
                        
                        # Pobranie dotychczasowej daty
                        domyslna_data = date.today()
                        if zgl.get("data_zgloszenia"):
                            try:
                                domyslna_data = datetime.strptime(str(zgl.get("data_zgloszenia")), "%Y-%m-%d").date()
                            except ValueError:
                                pass
                        nowa_data = st.date_input("Data zgłoszenia", value=domyslna_data, key=f"data_{zgl_id}")
                        
                        nowy_koszt = st.number_input("Koszt (zł)", value=float(zgl.get("koszt") or 0.0), min_value=0.0, step=10.0, key=f"koszt_{zgl_id}")
                        
                        opcje_statusu = ["Zgłoszone", "W trakcie naprawy", "Zakończone", "Anulowane"]
                        obecny_status = zgl.get("status", "Zgłoszone")
                        index_statusu = opcje_statusu.index(obecny_status) if obecny_status in opcje_statusu else 0
                        nowy_status = st.selectbox("Status", opcje_statusu, index=index_statusu, key=f"status_{zgl_id}")

                        btn_zapisz_edycje = st.form_submit_button("Zapisz zmiany")

                        if btn_zapisz_edycje:
                            try:
                                supabase.table("serwis").update({
                                    "opis": nowy_opis,
                                    "data_zgloszenia": str(nowa_data),
                                    "koszt": nowy_koszt,
                                    "status": nowy_status
                                }).eq("id", zgl_id).execute()
                                
                                st.success("Pomyślnie zaktualizowano zgłoszenie!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Błąd podczas aktualizacji: {err}")

            st.divider()
    else:
        st.info("Brak zgłoszeń serwisowych w bazie.")

# --- ZAKŁADKA 3: DODAWANIE SPRZĘTU ---
with tab3:
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
