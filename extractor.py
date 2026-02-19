import asyncio
from playwright.async_api import async_playwright

async def prueba_especifica():
    # El enlace que me pasaste
    url_test = "https://istreameast.is/links/paok-vs-celta-vigo-2425786"
    archivo_m3u = "prueba_individual.m3u"
    enlaces_encontrados = []

    async with async_playwright() as p:
        # Lanzamos el navegador
        browser = await p.chromium.launch(headless=False) # Ponemos False para que veas lo que hace en tu PC
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = await context.new_page()

        # Interceptor de red para capturar los .m3u8 maestros
        def interceptar(request):
            url = request.url
            if ".m3u8" in url and "index" in url and "chunk" not in url:
                if url not in enlaces_encontrados:
                    enlaces_encontrados.append(url)
                    print(f"\n[DETECTADO] Enlace M3U8: {url}\n")

        page.on("request", interceptar)

        try:
            print(f"Abriendo evento: {url_test}")
            await page.goto(url_test, wait_until="domcontentloaded")
            
            # Esperar 15 segundos para capturar el servidor principal automáticamente
            print("Esperando stream del servidor principal...")
            await asyncio.sleep(15)

            # Intentar capturar el "Server 2" (Backup)
            print("Buscando botón de 'Server 2'...")
            boton_backup = await page.get_by_text("Server 2", exact=True)
            
            if await boton_backup.is_visible():
                print("Haciendo clic en Server 2 para capturar respaldo...")
                # Usamos force=True porque a veces hay capas transparentes de publicidad
                await boton_backup.click(force=True)
                await asyncio.sleep(15)
            else:
                print("No se visualizó el botón de Server 2.")

        except Exception as e:
            print(f"Error durante la prueba: {e}")

        await browser.close()

    # Guardar resultado en archivo local
    if enlaces_encontrados:
        with open(archivo_m3u, "w") as f:
            f.write("#EXTM3U\n")
            for i, link in enumerate(enlaces_encontrados):
                f.write(f"#EXTINF:-1, Prueba PAOK-Celta (Servidor {i+1})\n")
                f.write(link + "\n")
        print(f"PRUEBA FINALIZADA: Se guardaron {len(enlaces_encontrados)} enlaces en '{archivo_m3u}'")
    else:
        print("PRUEBA FALLIDA: No se capturó ningún enlace .m3u8")

asyncio.run(prueba_especifica())
