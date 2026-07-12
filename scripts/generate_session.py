"""
scripts/generate_session.py
----------------------------
Corre este script en TU COMPUTADOR (no en GitHub Actions) cada vez que
necesites crear o renovar la sesión guardada.

Qué hace:
1. Abre una ventana real de Chrome.
2. Tú te logueas a mano en Moxfield (como cualquier persona).
3. Guarda las cookies/sesión en scripts/session.json.

Ese archivo NUNCA debe subirse al repo (está en .gitignore). Su contenido
lo vas a copiar como un GitHub Secret en el Paso 3.

Uso:
    python scripts/generate_session.py
"""

from playwright.sync_api import sync_playwright

SESSION_FILE = "session.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.moxfield.com/account/signin")

        print("\n" + "=" * 60)
        print("Se abrió una ventana de Chrome.")
        print("1. Inicia sesión manualmente en Moxfield.")
        print("2. Espera a que cargue tu perfil/dashboard.")
        print("3. Vuelve a esta terminal y presiona ENTER.")
        print("=" * 60 + "\n")
        input("Presiona ENTER cuando ya hayas iniciado sesión... ")

        context.storage_state(path=SESSION_FILE)
        print(f"\n✅ Sesión guardada en '{SESSION_FILE}'.")
        print("Siguiente paso: copiarla como GitHub Secret (ver instrucciones).")

        browser.close()


if __name__ == "__main__":
    main()
