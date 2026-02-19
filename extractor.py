import asyncio
from playwright.async_api import async_playwright

async def prueba_especifica():
    # URL del evento específico que pediste
    url_test = "https://istreameast.is/links/paok-vs-celta-vigo-2425786"
    archivo_m3u = "lista.m3u"
    enlaces_encontrados = []

    async with async_playwright() as p:
        # headless=True es obligatorio para GitHub Actions
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Capturador de enlaces m3u8
        def interceptar(request):
            url = request.url
            if ".m3u8" in url and "index" in url and "chunk" not in url:
                if url not in enlaces_encontrados:
                    enlaces_encontrados.append(url)
                    print(f"Detectado: {url}")

        page.on("request", interceptar)

        try:
            print(f"Iniciando extracción en: {url_test}")
            await page.goto(url_test, wait_until="domcontentloaded", timeout=60000)
            
            # Esperar al Servidor Principal
            await asyncio.sleep(20)

            # Intentar capturar el "Server 2" (Backup)
            print("Buscando botón de Server 2...")
            # Usamos un selector de texto flexible para encontrar el botón
            boton_backup = page.get_by_text("Server 2")
            if await boton_backup.is_visible():
                print("Cambiando a Server 2...")
                await boton_backup.click(force=True)
                await asyncio.sleep(20)

        except Exception as e:
            print(f"Error: {e}")

        await browser.close()

    # Siempre escribir el archivo para que el commit de GitHub no falle
    with open(archivo_m3u, "w") as f:
        f.write("#EXTM3U\n")
        if enlaces_encontrados:
            for i, link in enumerate(enlaces_encontrados):
                f.write(f"#EXTINF:-1, PAOK vs Celta - Servidor {i+1}\n")
                f.write(link + "\n")
        else:
            f.write("#EXTINF:-1, Stream no disponible actualmente\n")
            f.write("http://0.0.0.0/offline.mp4\n")

if __name__ == "__main__":
    asyncio.run(prueba_especifica())
