import asyncio
from playwright.async_api import async_playwright
import os

async def generar_m3u():
    url_evento = "https://crackstreams1.ws/nba-streams/" # Ajusta según lo que necesites
    archivo_m3u = "lista.m3u"
    
    # Iniciamos el navegador
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Buscando stream en: {url_evento}...")
        
        # Variable para guardar el enlace encontrado
        enlace_final = None

        # Interceptamos las peticiones para encontrar el .m3u8
        def interceptar_peticion(request):
            nonlocal enlace_final
            if ".m3u8" in request.url:
                enlace_final = request.url

        page.on("request", interceptar_peticion)
        
        try:
            await page.goto(url_evento, timeout=60000)
            # Esperamos un tiempo prudencial para que cargue el reproductor
            await asyncio.sleep(20) 
        except Exception as e:
            print(f"Error: {e}")
        
        await browser.close()

        # Si encontramos enlace, creamos el archivo M3U
        if enlace_final:
            print(f"¡Enlace encontrado! Guardando en {archivo_m3u}")
            with open(archivo_m3u, "w") as f:
                f.write("#EXTM3U\n")
                f.write(f"#EXTINF:-1, Evento Crackstreams\n")
                f.write(enlace_final)
        else:
            print("No se encontró enlace .m3u8")

asyncio.run(generar_m3u())