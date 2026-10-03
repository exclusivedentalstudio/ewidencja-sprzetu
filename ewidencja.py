import hashlib
import io
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from supabase import create_client

# -------------------------------------------------------------
# KONFIGURACJA STRONY I BAZY DANYCH
# -------------------------------------------------------------
st.set_page_config(
    page_title="Ewidencja Sprzętu Medycznego",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Pobieranie danych dostępowych z Secrets lub domyślne (do testów lokalnych)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def init_supabase():
  if not SUPABASE_URL or not SUPABASE_KEY:
    return None
  try:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
  except Exception as e:
    st.error(f"Błąd połączenia z bazą Supabase: {e}")
    return None


supabase = init_supabase()


# -------------------------------------------------------------
# FUNKCJE POMOCNICZE BAZY DANYCH
# -------------------------------------------------------------
def wczytaj_dane():
  """Wczytuje sprzęt z bazy Supabase lub pamięci tymczasowej."""
  if supabase:
    try:
      response = (
          supabase.table("sprzet")
          .select("*")
          .order("created_at", desc=True)
          .execute()
      )
      return response.data
    except Exception as e:
      st.error(f"Błąd wczytywania danych z chmury: {e}")
      return []
  else:
    if "lokalny_sprzet" not in st.session_state:
      st.session_state.lokalny_sprzet = []
    return st.session_state.lokalny_sprzet


def zapisz_dane(nowy_item):
  """Zapisuje sprzęt do bazy Supabase lub lokalnie."""
  if supabase:
    try:
      supabase.table("sprzet").insert(nowy_item).execute()
      return True
    except Exception as e:
      st.error(f"Błąd zapisu do chmury: {e}")
      return False
  else:
    st.session_state.lokalny_sprzet.append(nowy_item)
    return True


def wylicz_date_gwarancji(data_zakupu, miesiace_gwarancji):
  try:
    data_poczatek = datetime.strptime(str(data_zakupu), "%Y-%m-%d")
    data_konca = data_poczatek + timedelta(days=miesiace_gwarancji * 30)
    return data_konca.strftime("%Y-%m-%d")
  except Exception:
    return ""


def wylicz_najblizszy_przeglad(data_zakupu):
  try:
    dzis = datetime.now()
    data_zakup = datetime.strptime(str(data_zakupu), "%Y-%m-%d")
    nastepny = data_zakup
    while nastepny < dzis:
      nastepny += timedelta(days=365)
    return nastepny.strftime("%Y-%m-%d")
  except Exception:
    return ""


# -------------------------------------------------------------
# LOGOWANIE PRACOWNIKÓW
# -------------------------------------------------------------
# Przykładowa lista użytkowników (Login: Hasło)
# Hasła są zahashowane funkcją SHA-256 dla bezpieczeństwa
UZYTKOWNICY = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "jan.kowalski": hashlib.sha256("haslo123".encode()).hexdigest(),
    "anna.nowak": hashlib.sha256("serwis2024".encode()).hexdigest(),
}


def sprawdz_haslo(login, haslo):
  haslo_hash = hashlib.sha256(haslo.encode()).hexdigest()
  return UZYTKOWNICY.get(login) == haslo_hash


if "zalogowany" not in st.session_state:
  st.session_state.zalogowany = False
if "uzytkownik" not in st.session_state:
  st.session_state.uzytkownik = ""

# Panel boczny – Logowanie / Wylogowanie
st.sidebar.title("👤 Panel Pracownika")

if not st.session_state.zalogowany:
  st.sidebar.subheader("Zaloguj się")
  input_login = st.sidebar.text_input("Login")
  input_haslo = st.sidebar.text_input("Hasło", type="password")
  if st.sidebar.button("Zaloguj"):
    if sprawdz_haslo(input_login, input_haslo):
      st.session_state.zalogowany = True
      st.session_state.uzytkownik = input_login
      st.sidebar.success(f"Zalogowano jako: {input_login}")
      st.rerun()
    else:
      st.sidebar.error("Błędny login lub hasło!")

  st.title("🏥 Ewidencja Sprzętu Medycznego")
  st.info(
      "🔒 Dostęp do systemu wymaga zalogowania. Zaloguj się w panelu bocznym,"
      " aby wyświetlić i edytować dane."
  )
  st.markdown("""
    **Przykładowe dane do logowania (testowe):**
    * Login: `admin` | Hasło: `admin123`
    * Login: `jan.kowalski` | Hasło: `haslo123`
    * Login: `anna.nowak` | Hasło: `serwis2024`
    """)
  st.stop()

# Jeśli zalogowany:
st.sidebar.write(f"Zalogowano: **{st.session_state.uzytkownik}**")
if st.sidebar.button("Wyloguj się"):
  st.session_state.zalogowany = False
  st.session_state.uzytkownik = ""
  st.rerun()

# Powiadomienie o stanie połączenia z chmurą
if not supabase:
  st.sidebar.warning(
      "⚠️ Brak połączonej bazy Supabase. Aplikacja działa tymczasowo w trybie"
      " lokalnym."
  )

# -------------------------------------------------------------
# GŁÓWNY INTERFEJS APULIKACJI
# -------------------------------------------------------------
st.title("🏥 Ewidencja Sprzętu Medycznego")

sprzet_lista = wczytaj_dane()

# Pobranie unikalnych wartości do list wyboru
unikalne_nazwy = sorted(
    list(set(item.get("nazwa", "") for item in sprzet_lista if item.get("nazwa")))
)
unikalne_firmy = sorted(
    list(
        set(
            item.get("zakupujacy", "")
            for item in sprzet_lista
            if item.get("zakupujacy")
        )
    )
)
unikalni_dostawcy = sorted(
    list(
        set(
            item.get("dostawca", "")
            for item in sprzet_lista
            if item.get("dostawca")
        )
    )
)

# -------------------------------------------------------------
# ALERTY I PRZYPOMNIENIA
# -------------------------------------------------------------
dzis_dt = datetime.now()
przypomnienia_gwarancja = []
przypomnienia_serwis = []

for item in sprzet_lista:
  if item.get("data_konca_gwarancji"):
    try:
      koniec_gwar_dt = datetime.strptime(
          item["data_konca_gwarancji"], "%Y-%m-%d"
      )
      dni_do_konca = (koniec_gwar_dt - dzis_dt).days
      if 0 <= dni_do_konca <= 30:
        przypomnienia_gwarancja.append(
            f"⚠️ **{item['nazwa']}** (S/N: {item['nr_seryjny']}) – gwarancja"
            f" kończy się za **{dni_do_konca} dni**"
            f" ({item['data_konca_gwarancji']})!"
        )
      elif dni_do_konca < 0:
        przypomnienia_gwarancja.append(
            f"🔴 **{item['nazwa']}** (S/N: {item['nr_seryjny']}) – gwarancja"
            f" wygasła **{-dni_do_konca} dni temu**"
            f" ({item['data_konca_gwarancji']})!"
        )
    except Exception:
      pass

  if item.get("wymaga_przegladu_rocznego") and item.get("nastepny_przeglad"):
    try:
      przeglad_dt = datetime.strptime(item["nastepny_przeglad"], "%Y-%m-%d")
      dni_do_przegladu = (przeglad_dt - dzis_dt).days
      if 0 <= dni_do_przegladu <= 30:
        przypomnienia_serwis.append(
            f"🔧 **{item['nazwa']}** (S/N: {item['nr_seryjny']}) – planowany"
            f" serwis roczny za **{dni_do_przegladu} dni**"
            f" ({item['nastepny_przeglad']})!"
        )
      elif dni_do_przegladu < 0:
        przypomnienia_serwis.append(
            f"🚨 **{item['nazwa']}** (S/N: {item['nr_seryjny']}) – upłynął"
            f" termin rocznego serwisu (**{item['nastepny_przeglad']}**)"
        )
    except Exception:
      pass

if przypomnienia_gwarancja or przypomnienia_serwis:
  st.subheader("🔔 Przypomnienia i Alerty")
  for msg in przypomnienia_gwarancja:
    st.warning(msg)
  for msg in przypomnienia_serwis:
    st.error(msg)
  st.markdown("---")

# -------------------------------------------------------------
# FORMULARZ DODAWANIA SPRZĘTU
# -------------------------------------------------------------
with st.expander("➕ Dodaj nowy sprzęt", expanded=False):
  with st.form("form_dodaj"):
    col1, col2, col3 = st.columns(3)

    with col1:
      wybor_nazwy = st.selectbox(
          "Nazwa sprzętu (wybierz lub wpisz nową)",
          ["-- Wpisz nową nazwę --"] + unikalne_nazwy,
      )
      if wybor_nazwy == "-- Wpisz nową nazwę --":
        nazwa = st.text_input("Wpisz nazwę nowego sprzętu *")
      else:
        nazwa = wybor_nazwy

      nr_seryjny = st.text_input("Numer seryjny *")
      data_zakupu = st.date_input("Data zakupu", format="DD.MM.YYYY")

      wybor_firmy = st.selectbox(
          "Firma kupująca (wybierz lub dodaj nową)",
          ["-- Wpisz nową --"] + unikalne_firmy,
      )
      if wybor_firmy == "-- Wpisz nową --":
        zakupujacy = st.text_input("Wpisz nową firmę kupującą")
      else:
        zakupujacy = wybor_firmy

    with col2:
      wybor_dostawcy = st.selectbox(
          "Dostawca / Sprzedawca (wybierz lub dodaj nowego)",
          ["-- Wpisz nowego --"] + unikalni_dostawcy,
      )
      if wybor_dostawcy == "-- Wpisz nowego --":
        dostawca = st.text_input("Wpisz nowego dostawcę / sprzedawcę")
      else:
        dostawca = wybor_dostawcy

      lokalizacja = st.text_input("Obecna lokalizacja")
      status = st.selectbox(
          "Status", ["W użytku", "W naprawie", "Wycofany"]
      )
      gwarancja_miesiace = st.number_input(
          "Gwarancja (liczba miesięcy)", min_value=0, value=24, step=6
      )
      wymaga_przegladu = st.checkbox("Włącz coroczny serwis / przegląd", value=True)

    with col3:
      naprawa_rodzaj = st.selectbox(
          "Rodzaj naprawy", ["Brak", "Gwarancyjna", "Płatna"]
      )
      naprawa_koszt = st.number_input("Koszt naprawy (zł)", min_value=0.0)
      naprawa_wysylka = st.date_input(
          "Data wysłania do naprawy", format="DD.MM.YYYY"
      )
      naprawa_powrot = st.date_input(
          "Data powrotu z naprawy", format="DD.MM.YYYY"
      )

    submitted = st.form_submit_button("Zapisz sprzęt")

    if submitted:
      if not nazwa or not nr_seryjny:
        st.error("Nazwa sprzętu i Numer Seryjny są wymagane!")
      else:
        koniec_gwar = wylicz_date_gwarancji(data_zakupu, gwarancja_miesiace)
        nastepny_przeglad = (
            wylicz_najblizszy_przeglad(data_zakupu) if wymaga_przegladu else ""
        )

        nowy = {
            "nazwa": nazwa,
            "nr_seryjny": nr_seryjny,
            "data_zakupu": data_zakupu.strftime("%Y-%m-%d"),
            "zakupujacy": zakupujacy,
            "dostawca": dostawca,
            "lokalizacja": lokalizacja,
            "status": status,
            "gwarancja_miesiace": int(gwarancja_miesiace),
            "data_konca_gwarancji": koniec_gwar,
            "wymaga_przegladu_rocznego": wymaga_przegladu,
            "nastepny_przeglad": nastepny_przeglad,
            "naprawa_rodzaj": naprawa_rodzaj,
            "naprawa_koszt": float(naprawa_koszt),
            "naprawa_wysylka": naprawa_wysylka.strftime("%Y-%m-%d"),
            "naprawa_powrot": naprawa_powrot.strftime("%Y-%m-%d"),
            "dodal_uzytkownik": st.session_state.uzytkownik,
        }

        if zapisz_dane(nowy):
          st.success("Sprzęt został pomyślnie dodany do bazy danych!")
          st.rerun()

# -------------------------------------------------------------
# WYSZUKIWARKA I LISTA SPRZĘTU
# -------------------------------------------------------------
st.subheader("📋 Baza sprzętu medycznego")

if sprzet_lista:
  df = pd.DataFrame(sprzet_lista)

  # Usuwamy wewnętrzne kolumny Supabase z widoku tabeli, jeśli istnieją
  df_display = df.drop(
      columns=["id", "created_at"], errors="ignore"
  )

  col_search1, col_search2 = st.columns([3, 1])
  with col_search1:
    szukaj = st.text_input(
        "🔍 Wyszukaj (nazwa, nr seryjny, lokalizacja, firma...):"
    )
  with col_search2:
    filtr_status = st.multiselect(
        "Filtruj status:",
        options=(
            list(df_display["status"].unique())
            if "status" in df_display.columns
            else []
        ),
        default=[],
    )

  df_filtered = df_display.copy()

  if szukaj:
    szukaj_lower = szukaj.lower()
    df_filtered = df_filtered[
        df_filtered.apply(
            lambda row: any(
                szukaj_lower in str(val).lower() for val in row.values
            ),
            axis=1,
        )
    ]

  if filtr_status:
    df_filtered = df_filtered[df_filtered["status"].isin(filtr_status)]

  st.dataframe(df_filtered, use_container_width=True)

  buffer = io.BytesIO()
  with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_display.to_excel(writer, index=False, sheet_name="Sprzet_Medyczny")

  st.download_button(
      label="📥 Pobierz całą bazę do pliku Excel (.xlsx)",
      data=buffer.getvalue(),
      file_name="Ewidencja_Sprzetu_Medycznego.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )
else:
  st.info("Baza danych jest obecnie pusta. Dodaj pierwszy sprzęt powyżej.")