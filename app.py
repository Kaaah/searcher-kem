import streamlit as st
import requests
import re

st.title("Comparar cartas con colección Moxfield")

# Textarea para pegar la lista
text_input = st.text_area("Pega tu lista de cartas (ej: '4 Lightning Bolt')", height=300)

if text_input:
    # Extraer nombres ignorando la cantidad al inicio
    pattern = re.compile(r"^\s*\d*\s*(.+)", re.IGNORECASE)
    user_cards = set()

    for line in text_input.splitlines():
        match = pattern.match(line.strip())
        if match:
            card_name = match.group(1).strip().lower()
            if card_name:
                user_cards.add(card_name)

    # Descargar colección desde Moxfield
    binder_url = "https://api2.moxfield.com/v2/binder/goU3_MIYFk67LHij1E7dPQ"
    response = requests.get(binder_url)

    if response.status_code == 200:
        binder_data = response.json()
        binder_cards = {entry["card"]["name"].lower() for entry in binder_data["cards"].values()}

        # Comparar
        comunes = sorted(user_cards & binder_cards)

        st.success(f"Se encontraron {len(comunes)} cartas en común.")
        st.write(comunes)
    else:
        st.error("No se pudo obtener la colección desde Moxfield.")
