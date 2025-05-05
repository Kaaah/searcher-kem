import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO, BytesIO

# --- URL del CSV desde GitHub ---
CSV_URL = "https://raw.githubusercontent.com/Kaaah/searcher-kem/main/mi_coleccion.csv"

# --- TÍTULO E INSTRUCCIONES ---
st.title("🧙‍♂️ Comparar tu lista con mi colección")
st.markdown("""
Pega tu lista de cartas en cualquiera de estos formatos:

**Formato simple:**
4 Lightning Bolt
2 Llanowar Elves

**Formato tipo Manabox (funciona con o sin número al final):**
1 Diabolic Intent (PBRO) 89p
1 Deadly Dispute (P30A) 29 F
1 Gray Merchant of Asphodel (THS)

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
        df = pd.read_csv(csv_data, usecols=["Name", "Edition", "Language", "Count"])
        df["name_lower"] = df["Name"].str.lower()
    except Exception as e:
        st.error(f"❌ Error al cargar la colección: {e}")
        st.stop()

    # Regex mejorada para extraer nombre de la carta
    pattern = re.compile(
        r"^\s*\d+\s+(.+?)(?:\s+\(.*?\)|\s+[A-Z]{2,5}-\d+\w*|\s+\*F\*|\s+p|\s+\d+)*\s*$", 
        re.IGNORECASE
    )

    user_cards = set()
    detected_names = []
    for line in user_input.splitlines():
        match = pattern.match(line.strip())
        if match:
            name = match.group(1).strip()
            if name:
                detected_names.append(name)
                user_cards.add(name.lower())

    if not user_cards:
        st.warning("⚠️ No se detectaron nombres válidos.")
        st.stop()

    # Comparar con la colección
    coincidencias = df[df["name_lower"].isin(user_cards)]

    if not coincidencias.empty:
        # Agrupar y sumar cantidades por carta, edición e idioma
        coincidencias = (
            coincidencias
            .groupby(["Name", "Edition", "Language"], as_index=False)
            .agg({"Count": "sum"})
        )

        # Renombrar columnas
        coincidencias.columns = ["Nombre", "Edición", "Idioma", "Cantidad en Stock"]

        # Convertir edición a mayúsculas
        coincidencias["Edición"] = coincidencias["Edición"].str.upper()

        st.success(f"✅ Se encontraron {len(coincidencias)} cartas en común.")
        st.dataframe(coincidencias)

        # Crear archivo Excel para descargar
        output = BytesIO()
        coincidencias.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        st.download_button(
            label="📥 Descargar como Excel",
            data=output,
            file_name="cartas_en_comun.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("❌ No hay coincidencias con tu colección.")
