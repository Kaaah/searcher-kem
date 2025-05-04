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
    # --- Leer CSV desde GitHub ---
    try:
        coleccion_df = pd.read_csv(CSV_URL)
        coleccion_df["name_lower"] = coleccion_df["Name"].str.lower()
    except Exception as e:
        st.error(f"❌ Error al cargar la colección desde GitHub: {e}")
        st.stop()

    # --- Procesar entrada del usuario ---
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

    # --- Comparación ---
    coincidencias = coleccion_df[coleccion_df["name_lower"].isin(user_cards)]

    # --- Mostrar resultados ---
    if not coincidencias.empty:
        st.success(f"✅ Se encontraron {len(coincidencias)} cartas en común.")
        st.dataframe(coincidencias[["Name", "Language", "Count", "Purchase Price"]])

        # Descargar
        st.download_button(
            label="📥 Descargar como Excel",
            data=coincidencias[["Name", "Language", "Count", "Purchase Price"]].to_excel(index=False, engine='openpyxl'),
            file_name="cartas_en_comun.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("❌ No hay coincidencias.")
