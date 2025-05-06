import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO, BytesIO

# --- CONFIGURACIÓN ---
CSV_URL = "https://raw.githubusercontent.com/Kaaah/searcher-kem/main/mi_coleccion.csv"
NUMERO_TELEFONO = "56977130463"  # Reemplaza con tu número sin el "+"

# --- TÍTULO E INSTRUCCIONES ---
st.title("Kartas en Mano - Comparar lista de cartas 🧙‍♂️")

st.markdown("""
Pega tu lista de cartas aquí. Puedes usar formato libre o tipo Manabox:
**Formato simple:**
4 Lightning Bolt //
2 Llanowar Elves //

**Formato tipo Manabox (funciona con o sin número al final):**
1 Diabolic Intent (PBRO) 89p //
1 Deadly Dispute (P30A) 29 F //
1 Gray Merchant of Asphodel (THS) //

""")

# --- ENTRADA DEL USUARIO ---
user_input = st.text_area("📋 Lista de cartas:", height=300)

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

    # Regex para extraer nombres (ignora edición, número y flags)
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


    # --- COMPARACIÓN ---
    coincidencias = df[df["name_lower"].isin(user_cards)]

    if not coincidencias.empty:
        # Agrupar duplicados por carta/edición/idioma
        coincidencias = (
            coincidencias
            .groupby(["Name", "Edition", "Language"], as_index=False)
            .agg({"Count": "sum"})
        )

        # Renombrar columnas y formatear
        coincidencias.columns = ["Nombre", "Edición", "Idioma", "Cantidad en Stock"]
        coincidencias["Edición"] = coincidencias["Edición"].str.upper()

        st.success(f"✅ Se encontraron {len(coincidencias)} cartas en común.")
        st.dataframe(coincidencias)

        # --- Descargar como Excel ---
        output = BytesIO()
        coincidencias.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        st.download_button(
            label="📥 Descargar como Excel",
            data=output,
            file_name="cartas_en_comun.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # --- Generar mensaje WhatsApp ---
        lineas_mensaje = [f"Hola, se encontraron {len(coincidencias)} cartas en común:\n"]
        for _, row in coincidencias.iterrows():
            linea = f"- {row['Nombre']} ({row['Edición']}) - Idioma: {row['Idioma']} - Cantidad: {row['Cantidad en Stock']}"
            lineas_mensaje.append(linea)

        mensaje_completo = "\n".join(lineas_mensaje)
        mensaje_encoded = requests.utils.quote(mensaje_completo)

        whatsapp_url = f"https://wa.me/{NUMERO_TELEFONO}?text={mensaje_encoded}"

        st.markdown(f"[📤 Enviar mensaje por WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

    else:
        st.warning("❌ No se encontraron coincidencias con tu colección.")

# --- BOTÓN SIEMPRE VISIBLE: HACER PEDIDO ---
mensaje_pedido = "Hola Kartas en Mano, estoy buscando singles de Magic: The Gathering!"
mensaje_pedido_encoded = requests.utils.quote(mensaje_pedido)
url_pedido = f"https://wa.me/{NUMERO_TELEFONO}?text={mensaje_pedido_encoded}"

st.markdown("---")
st.markdown(
    f'<a href="{url_pedido}" target="_blank"><button style="background-color:#25D366;color:white;padding:10px 20px;border:none;border-radius:8px;font-size:16px;cursor:pointer;">🧾 Hacer Pedido!</button></a>',
    unsafe_allow_html=True
)

