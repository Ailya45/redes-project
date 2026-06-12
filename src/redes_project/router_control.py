# src/redes_project/router_control.py
import time

from playwright.sync_api import sync_playwright

ROUTER_IP = "192.168.0.1"  # IP de tu Archer C50
USER = "admin"
PASS = "oro29$$87*"         # Tu contraseña real del router
BASE_URL = f"http://{ROUTER_IP}"

class TPLinkController:
    def __init__(self):
        pass

    def agregar_a_lista_negra(self, mac_address):
        """Abre el navegador, hace login y añade la MAC a la lista negra."""
        print(f"[RPA-ROUTER] Iniciando proceso de expulsión para MAC: {mac_address}")

        # Formateamos la MAC para evitar conflictos
        mac_formateada = mac_address.replace(":", "-").upper()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            try:
                # 1. IR AL ROUTER Y HACER LOGIN
                page.goto(BASE_URL, timeout=10000)
                page.fill("input[type='password']", PASS)
                page.click("button#login-btn, input[type='submit'], .login-button, a.button-button")
                page.wait_for_load_state("networkidle")

                # 2. NAVEGAR AL MENÚ DE FILTRADO MAC
                page.click("text=Avanzado", timeout=5000)
                page.click("text=Seguridad", timeout=5000)
                page.click("text=Control de Acceso", timeout=5000)

                # 3. AGREGAR LA MAC
                page.click("text=Agregar", timeout=5000)

                # Cliquear la card de la MAC dinámica
                page.click(f"span.content:has-text('{mac_formateada}')", timeout=5000)

                # Guardar cambios (Botón Añadir)
                page.click("a.button-button:has-text('AÑADIR')", timeout=5000)

                time.sleep(2)
                print(f"[RPA-ROUTER] ✓ MAC {mac_address} bloqueada exitosamente.")
                return True

            except Exception as e:
                print(f"[RPA-ROUTER ERROR] Falló la automatización de bloqueo: {e}")
                return False
            finally:
                browser.close()

    def remover_de_lista_negra(self, mac_address):
        """Abre el navegador, busca la MAC en la tabla y la elimina de forma sincrónica."""
        print(f"[RPA-ROUTER] Iniciando remoción de penalización para MAC: {mac_address}")

        # Formateamos la MAC con guiones y mayúsculas
        mac_formateada = mac_address.replace(":", "-").upper()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            try:
                # 1. LOGIN
                page.goto(BASE_URL, timeout=10000)
                page.fill("input[type='password']", PASS)
                page.click("button#login-btn, input[type='submit'], .login-button, a.button-button")
                page.wait_for_load_state("networkidle")

                # 2. NAVEGAR AL FILTRO
                page.click("text=Avanzado", timeout=5000)
                page.click("text=Seguridad", timeout=5000)
                page.click("text=Control de Acceso", timeout=5000)

                # 3. LOCALIZAR Y ELIMINAR LA FILA DE LA MAC
                fila = page.locator(f"tr:has-text('{mac_formateada}')")

                try:
                    # Forzamos a Playwright síncrono a esperar que la fila sea visible de verdad
                    fila.wait_for(state="visible", timeout=4000)

                    # Hacemos clic en el botón exacto con la clase que inspeccionamos antes
                    print(f"[RPA-ROUTER] Fila encontrada para {mac_formateada}. Presionando botón de eliminar...")
                    fila.locator("a.grid-content-btn.btn-delete").first.click()

                    # Esperamos que la fila desaparezca para confirmar que se eliminó correctamente
                    fila.wait_for(state="detached", timeout=5000)
                    print(f"[RPA-ROUTER] ✓ MAC {mac_address} removida de la lista negra.")
                    return True

                except Exception:
                    # Si el wait_for da Timeout, significa que la fila no existe en la tabla
                    print(f"[RPA-ROUTER AVISO] La MAC {mac_formateada} no se encontró en la lista negra.")
                    return True  # Retornamos True porque operativamente ya no está bloqueada

            except Exception as e:
                print(f"[RPA-ROUTER ERROR] Falló la automatización de remoción: {e}")
                return False
            finally:
                browser.close()
