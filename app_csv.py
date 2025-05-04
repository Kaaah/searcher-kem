import streamlit as st
import pandas as pd
import requests
import re

# --- CONFIGURACIÓN ---
CSV_URL = "https://github.com/Kaaah/searcher-kem/blob/main/mi_coleccion.csv"#"https://raw.githubusercontent.com/tuusuario/tu-repo/main/mi_coleccion.csv" 

# --- STREAMLIT INTERFAZ ---
st.title("🧙‍♂️ Comparar tu lista con mi colección (desde GitHub)")

st.markdown("""
Pega tu lista de cartas con este formato:

4 Lightning Bolt
2 Llanowar Elves
1 Sol Ring

""")

user_input = st.text_area("📋 Pega tu lista aquí:", height=300)

if st.button("🔍 Comparar") and user_input.strip():
    try:
        # Descargar el CSV completo como texto
        response = requests.get(CSV_URL)
        response.raise_for_status()
        csv_data = StringIO(response.text)

        # Leer sólo las columnas necesarias
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

    # Comparar con colección
    coincidencias = df[df["name_lower"].isin(user_cards)]

    # Mostrar resultados
    if not coincidencias.empty:
        st.success(f"✅ Se encontraron {len(coincidencias)} cartas en común.")
        st.dataframe(coincidencias[["Name", "Language", "Count", "Purchase Price"]])

        st.download_button(
            label="📥 Descargar como Excel",
            data=coincidencias[["Name", "Language", "Count", "Purchase Price"]].to_excel(index=False, engine='openpyxl'),
            file_name="cartas_en_comun.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("❌ No hay coincidencias.")
