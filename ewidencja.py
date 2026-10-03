import streamlit as st
from supabase import create_client

# 1. Połączenie z Supabase (skorzystaj ze swoich istniejących danych dostępów)
supabase = create_client("https://wfcchwwfikmjpevlfnms.supabase.co","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndmY2Nod3dmaWttanBldmxmbm1zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEwMjIwMDIsImV4cCI6MjEwNjU5ODAwMn0.rJbsuf60L46ph-24cnbD4vPfqIaTymrczMzw_Wovp5E")

st.title("Ewidencja Sprzętu Medycznego")

# Tworzymy zakładki
tab_lista, tab_nowy_serwis, tab_historia = st.tabs([
    "📦 Lista sprzętu", 
    "🛠️ Oddaj do serwisu / Odbierz", 
    "📋 Karta sprzętu i historia"
])

# --- ZAKŁADKA 1: LISTA SPRZĘTU ---
with tab_lista:
    st.header("Sprzęt w bazie")
    # Kod do wyświetlania tabeli ze sprzętem...

# --- ZAKŁADKA 2: ODDAJ / ODBIERZ Z SERWISU ---
with tab_nowy_serwis:
    st.header("Zgłoszenie lub zamknięcie serwisu")
    
    st.subheader("1. Wyszlij sprzęt do serwisu")
    # Pobieramy sprzęt z bazy do wyboru
    sprzet_list = supabase.table("sprzet").select("id, nazwa, numer_seryjny").execute().data
    
    if sprzet_list:
        wybrany = st.selectbox(
            "Wybierz sprzęt do wysłania:", 
            sprzet_list, 
            format_func=lambda x: f"{x['nazwa']} (SN: {x.get('numer_seryjny', 'Brak')})"
        )
        
        with st.form("form_oddaj_do_serwisu"):
            firma_serwis = st.text_input("Firma serwisowa / Serwis zewnętrzny")
            opis_usterki = st.text_area("Opis usterki / Rodzaj naprawy")
            data_zgloszenia = st.date_input("Data zgłoszenia")
            
            submitted = st.form_submit_button("Wyślij do serwisu")
            if submitted:
                data_serwisu = {
                    "sprzet_id": wybrany["id"],
                    "nazwa_sprzetu": wybrany["nazwa"],
                    "numer_seryjny": wybrany.get("numer_seryjny"),
                    "serwis_firma": firma_serwis,
                    "rodzaj_naprawy": opis_usterki,
                    "data_zgloszenia": str(data_zgloszenia),
                    "status_serwisu": "W naprawie"
                }
                supabase.table("serwis").insert(data_serwisu).execute()
                st.success(f"Dodano wpis serwisowy dla firmy: {firma_serwis}")

# --- ZAKŁADKA 3: KARTA SPRZĘTU I HISTORIA ---
with tab_historia:
    st.header("📋 Karta sprzętu i historia napraw")

    if sprzet_list:
        wybrana_pozycja = st.selectbox(
            "Wybierz sprzęt z bazy, aby zobaczyć historię:", 
            sprzet_list, 
            format_func=lambda x: f"{x['nazwa']} (SN: {x.get('numer_seryjny', 'Brak')})",
            key="historia_select"
        )

        sprzet_id = wybrana_pozycja["id"]

        # 1. Szczegóły wybranego sprzętu
        szczegoly = supabase.table("sprzet").select("*").eq("id", sprzet_id).execute().data[0]
        st.subheader(f"Szczegóły: {szczegoly['nazwa']}")
        
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Dostawca:** {szczegoly.get('dostawca', 'Brak')}")
        col2.write(f"**Data zakupu:** {szczegoly.get('data_zakupu', 'Brak')}")
        col3.write(f"**Firma (faktura):** {szczegoly.get('na_jaka_firme', 'Brak')}")

        st.divider()

        # 2. Wyświetlenie całej historii serwisowej
        st.subheader("🛠️ Historia serwisowa")
        historie = supabase.table("serwis").select("*").eq("sprzet_id", sprzet_id).order("data_zgloszenia", desc=True).execute().data

        if historie:
            for entry in historie:
                with st.expander(f"🔧 {entry['data_zgloszenia']} – {entry['serwis_firma']} ({entry['status_serwisu']})"):
                    st.write(f"**Firma serwisowa:** {entry['serwis_firma']}")
                    st.write(f"**Rodzaj naprawy / usterka:** {entry['rodzaj_naprawy']}")
                    st.write(f"**Data zgłoszenia:** {entry['data_zgloszenia']}")
                    st.write(f"**Data powrotu:** {entry.get('data_powrotu') or 'W trakcie naprawy'}")
                    st.write(f"**Koszt:** {entry.get('koszt_naprawy') or 0} PLN")
                    st.write(f"**Uwagi:** {entry.get('uwagi_serwisowe') or 'Brak'}")
        else:
            st.info("Ten sprzęt nie posiada jeszcze historii napraw.")
