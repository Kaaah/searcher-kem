import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO, BytesIO

# --- URL del CSV desde GitHub (raw) ---
CSV_URL = "https://raw.githubusercontent.com/Kaaah/searcher-kem/main/mi_coleccion.csv"

# --- TÍTULO E INSTRUCCIONES ---
st.title("🧙‍♂️ Comparar tu lista con mi colección")
st.markdown("""
Pega tu lista de cartas en el siguiente formato:



4 Lightning Bolt
2 Llanowar Elves
1 Sol Ring

Solo el nombre importa, el número puede ir o no.
""")

# --- ENTRADA DEL USUARIO ---
user_input = st.text_area("📋 Pega tu lista aquí:", height=300)

# --- BOTÓN DE COMPARAR ---
if st.button("🔍 Comparar") and user_input.strip():
    try:
        # Descargar CSV desde GitHub
        response = requests.get(CSV_URL)
        response.raise_for_status()
        csv_data = StringIO(response.text)

        # Leer columnas necesarias
        df = pd.read_csv(csv_data, usecols=["Name", "Language", "Count", "Purchase Price"])
        df["name_lower"] = df["Name"].str.lower()
    except Exception as e:
        st.error(f"❌ Error al cargar la colección: {e}")
        st.stop()

    # Procesar entrada del usuario
    pattern = re.compile(r"^\s*\d*\s*(.+)", re.IGNORECASE)
    user_cards = set()

    for line in user_input.splitlines():
        match = pattern.match(line.strip())
        if match:
            name = match.group(1).strip().lower()
            if name:
                user_cards.add(name)

    if not user_cards:
        st.warning("⚠️ No se detectaron nombres válidos.")
        st.stop()

    # Comparar con la colección
    coincidencias = df[df["name_lower"].isin(user_cards)]

    # Mostrar resultados
    if not coincidencias.empty:
        st.success(f"✅ Se encontraron {len(coincidencias)} cartas en común.")
        st.dataframe(coincidencias[["Name", "Language", "Count", "Purchase Price"]])

        # Generar archivo Excel en memoria
        output = BytesIO()
        coincidencias[["Name", "Language", "Count", "Purchase Price"]].to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        # Botón de descarga
        st.download_button(
            label="📥 Descargar como Excel",
            data=output,
            file_name="cartas_en_comun.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("❌ No hay coincidencias con tu colección.")
