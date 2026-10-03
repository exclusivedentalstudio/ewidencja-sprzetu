import streamlit as st
from supabase import create_client

# Zapisu nowego zgłoszenia serwisowego
def oddaj_do_serwisu(sprzet_id, nazwa, numer_seryjny, firma_serwisowa, opis_usterki, data_zgloszenia):
    data = {
        "sprzet_id": sprzet_id,
        "nazwa_sprzetu": nazwa,
        "numer_seryjny": numer_seryjny,
        "serwis_firma": firma_serwisowa,  # Zapamiętuje firmę serwisową
        "rodzaj_naprawy": opis_usterki,
        "data_zgloszenia": str(data_zgloszenia),
        "status_serwisu": "W naprawie"
    }
    supabase.table("serwis").insert(data).execute()
    st.success(f"Sprzęt wysłany do serwisu: {firma_serwisowa}")

# Aktualizacja po powrocie z serwisu
def zamknij_serwis(serwis_id, data_powrotu, koszt, uwagi):
    data = {
        "status_serwisu": "Naprawiono",  # lub 'Zakończono'
        "data_powrotu": str(data_powrotu),
        "koszt_naprawy": koszt,
        "uwagi_serwisowe": uwagi
    }
    supabase.table("serwis").update(data).eq("id", serwis_id).execute()
    st.success("Zaktualizowano historię serwisu!")
