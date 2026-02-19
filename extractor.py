import asyncio
from playwright.async_api import async_playwright

async def generar_m3u():
    url_principal = "https://crackstreams1.ws/" 
    archivo_m3u = "lista.m3u"
    enlaces_encontrados = []

    async with async_playwright() as p:
        # Lanzamos navegador con bloqueador de publicidad básico (evita popups)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = await context.new_page()

        # Interceptor para capturar los .m3u8 de ambos servidores
        def interceptar(request):
            url = request.url
            if ".m3u8" in url and "index" in url and "chunk" not in url:
                if url not in enlaces_encontrados:
                    enlaces_encontrados.append(url)
                    print(f"Enlace capturado: {url}")

        page.on("request", interceptar)

        try:
            print("Accediendo a Crackstreams...")
            await page.goto(url_principal, wait_until="domcontentloaded")

            # 1. Buscar evento LIVE
            await page.wait_for_selector("text=LIVE")
            primer_evento = await page.query_selector("a:has-text('LIVE')")
            
            if primer_evento:
                href = await primer_evento.get_attribute("href")
                url_evento = url_principal + href if href.startswith("/") else href
                print(f"Entrando al evento: {url_evento}")
                
                # 2. Ir a la página del stream (StreamEast)
                await page.goto(url_evento, wait_until="networkidle")
                
                # 3. Capturar Main Server (ya suele cargar solo)
                await asyncio.sleep(15) 

                # 4. Intentar capturar el Server 2 (Backup)
                print("Intentando cambiar al Server 2...")
                boton_server2 = await page.query_selector("text='Server 2'")
                if boton_server2:
                    # Hacemos clic (Playwright suele saltarse los popups de click)
                    await boton_server2.click()
                    await asyncio.sleep(15)

        except Exception as e:
            print(f"Error: {e}")

        await browser.close()

    # Escribir la lista M3U con los enlaces encontrados
    with open(archivo_m3u, "w") as f:
        f.write("#EXTM3U\n")
        if enlaces_encontrados:
            for i, link in enumerate(enlaces_encontrados):
                nombre = "Principal" if i == 0 else f"Backup {i}"
                f.write(f"#EXTINF:-1, Evento - Server {nombre}\n")
                f.write(link + "\n")
            print(f"Se guardaron {len(enlaces_encontrados)} enlaces.")
        else:
            f.write("#EXTINF:-1, Sin transmisiones activas\n")
            f.write("http://0.0.0.0/offline.mp4\n")

asyncio.run(generar_m3u())
