# frontend/frontend/frontend.py
import reflex as rx
import httpx
from .colores import *

class State(rx.State):
    current_page: str = "principal"
    username_input: str = ""
    password_input: str = ""
    token: str = ""
    error_login: str = ""
    fincas: list[dict] = []
    error_conexion: str = ""

    def set_username_input(self, value: str):
        self.username_input = value

    def set_password_input(self, value: str):
        self.password_input = value

    def login(self):
        try:
            response = httpx.post(
                "http://localhost:8000/api/login",
                data={"username": self.username_input, "password": self.password_input}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token", "")
                self.error_login = ""
                self.cargar_datos_dashboard()
            else:
                self.error_login = "Usuario o contraseña incorrectos"
        except Exception:
            self.error_login = "No se pudo conectar con el servidor backend"

    def cargar_datos_dashboard(self):
        if not self.token:
            return
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = httpx.get("http://localhost:8000/api/dashboard/summary", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.fincas = data.get("fincas", [])
                self.error_conexion = ""
            else:
                self.error_conexion = "Error al obtener los datos de la base de datos"
        except Exception:
            self.error_conexion = "Error de conexión con la base de datos"

    def set_page(self, page: str):
        self.current_page = page

def header_component():
    return rx.hstack(
        rx.text("🌱 AGROTECH - Control de Temperatura", color=TEXTO_PRINCIPAL, font_weight="bold"),
        rx.badge("CONECTADO A BD", background_color=VERDE, color="#04210F"),
        justify="between", width="100%", padding="1em 1.5em", background_color=PANEL,
    )

def vista_login():
    return rx.center(
        rx.vstack(
            rx.heading("Iniciar Sesión", color=TEXTO_PRINCIPAL, size="6"),
            rx.input(
                placeholder="Usuario", 
                value=State.username_input, 
                on_change=State.set_username_input,
                background_color=HUECO_DEPOSITO, color=TEXTO_PRINCIPAL
            ),
            rx.input(
                placeholder="Contraseña", 
                type="password", 
                value=State.password_input, 
                on_change=State.set_password_input,
                background_color=HUECO_DEPOSITO, color=TEXTO_PRINCIPAL
            ),
            rx.button("Entrar", on_click=State.login, background_color=VERDE, color="#04210F", width="100%"),
            rx.cond(State.error_login != "", rx.text(State.error_login, color=ROJO), rx.fragment()),
            spacing="3", padding="2em", background_color=PANEL, border_radius="10px", width="320px",
        ),
        background_color=FONDO_BASE, min_height="100vh", width="100%",
    )

def vista_principal():
    return rx.vstack(
        header_component(),
        rx.cond(State.error_conexion != "", rx.text(State.error_conexion, color=ROJO), rx.fragment()),
        rx.vstack(
            rx.heading("Fincas y Sensores en la Base de Datos", color=TEXTO_PRINCIPAL, size="5"),
            rx.foreach(
                State.fincas,
                lambda finca: rx.vstack(
                    rx.text(finca["name"], color=TEXTO_PRINCIPAL, font_weight="bold"),
                    rx.text(f"Ubicación: {finca['location']}", color=TEXTO_SECUNDARIO),
                    background_color=PANEL, padding="1em", border_radius="8px", width="100%",
                )
            ),
            spacing="3", width="100%", padding="2em", max_width="600px",
        ),
        background_color=FONDO_BASE, min_height="100vh", width="100%", align="center",
    )

def index():
    return rx.box(
        rx.cond(
            State.token == "",
            vista_login(),
            vista_principal(),
        ),
        background_color=FONDO_BASE, width="100%",
    )

app = rx.App()
app.add_page(index)