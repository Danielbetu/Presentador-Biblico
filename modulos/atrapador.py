import sys
import os
import traceback
import urllib.request
import json
import tkinter as tk

TELEGRAM_BOT_TOKEN = "8810989207:AAGXl6MLwZsAoY6Ys9ZD96pI3HWuUx9C0SQ"
TELEGRAM_CHAT_ID = "1395884678"

# Referencia global local para conectar con la app principal
_APP_INSTANCIA = None

TEXTOS = {
    "es": {
        "titulo": "Reporte de Sistema",
        "cuerpo": (
            "La aplicación experimentó un fallo inesperado y debe reiniciarse.\n\n"
            "El reporte técnico ha sido enviado de forma automática al desarrollador "
            "con los datos precisos del error, en estricto cumplimiento con las "
            "normativas internacionales de protección y privacidad de datos.\n\n"
            "No se ha adjuntado ningún tipo de información personal ni de sus archivos."
        ),
        "boton": "Reiniciar Aplicación"
    },
    "en": {
        "titulo": "System Report",
        "cuerpo": (
            "The application experienced an unexpected failure and needs to restart.\n\n"
            "The technical report has been automatically sent to the developer "
            "with precise error data, in strict compliance with international "
            "data protection and privacy regulations.\n\n"
            "No personal information or files have been attached."
        ),
        "boton": "Restart Application"
    },
    "por": {
        "titulo": "Relatório do Sistema",
        "cuerpo": (
            "A aplicação encontrou um erro inesperado e precisa ser reiniciada.\n\n"
            "O relatório técnico foi enviado automaticamente ao desenvolvedor "
            "com os dados precisos do erro, em estrito cumprimento das "
            "normas internacionais de proteção e privacidade de dados.\n\n"
            "Nenhuma informação pessoal ou arquivo foi anexado."
        ),
        "boton": "Reiniciar Aplicação"
    },
    "fr": {
        "titulo": "Rapport Système",
        "cuerpo": (
            "L'application a rencontré une erreur inattendue et doit redémarrer.\n\n"
            "Le rapport technique a été envoyé automatiquement au développeur "
            "avec les données précises de l'erreur, en strict respect des "
            "réglementations internationales sur la protection des données.\n\n"
            "Aucune information personnelle ni aucun fichier n'a été joint."
        ),
        "boton": "Redémarrer L'application"
    },
    "it": {
        "titulo": "Rapporto di Sistema",
        "cuerpo": (
            "L'applicazione ha riscontrato un errore imprevisto e deve essere riavviata.\n\n"
            "Il rapporto tecnico è stato inviato automaticamente allo sviluppatore "
            "con i dati precisi dell'errore, nel rispetto delle normative "
            "internazionali sulla protezione e la privacy dei dati.\n\n"
            "Nessuna informazione personale o file è stata allegata."
        ),
        "boton": "Riavvia Applicazione"
    }
}

def asociar_a_app(app_instancia):
    """Guarda la referencia a la app principal para consultar su idioma y capturar errores."""
    global _APP_INSTANCIA
    _APP_INSTANCIA = app_instancia
    if hasattr(app_instancia, "root"):
        app_instancia.root.report_callback_exception = lambda exc_type, exc_value, exc_traceback: _atrapador_de_errores(exc_type, exc_value, exc_traceback)

def _obtener_idioma_activo():
    """Busca el idioma en la app sin importar cómo se llame la variable ni cómo esté escrito."""
    global _APP_INSTANCIA
    if not _APP_INSTANCIA:
        return "en"

    # Mapeo universal de nombres y códigos
    mapa = {
        "es": "es", "spanish": "es", "español": "es", "espanol": "es",
        "en": "en", "english": "en", "ingles": "en", "inglés": "en",
        "por": "por", "portuguese": "por", "portugues": "por", "português": "por",
        "fr": "fr", "french": "fr", "frances": "fr", "français": "fr",
        "it": "it", "italian": "it", "italiano": "it", "italiano": "it"
    }

    # Recorremos todos los atributos de la app buscando alguno que contenga la palabra idioma o lang
    for attr in dir(_APP_INSTANCIA):
        if "idioma" in attr.lower() or "lang" in attr.lower():
            try:
                val = str(getattr(_APP_INSTANCIA, attr)).lower().strip()
                # 1. Probar palabra completa (ej: "portugues")
                if val in mapa:
                    return mapa[val]
                # 2. Probar primeras 2 letras (ej: "pt-BR" -> "pt")
                if val[:2] in mapa:
                    return mapa[val[:2]]
            except Exception:
                pass

    return "en"

def _reiniciar_aplicacion():
    """Reinicia el script ejecutable de Python de forma limpia."""
    python = sys.executable
    os.execv(python, [python] + sys.argv)

def _mostrar_pantalla_error_en_app():
    """Limpia la app principal y despliega la pantalla de aviso integrada."""
    global _APP_INSTANCIA
    if _APP_INSTANCIA and hasattr(_APP_INSTANCIA, "root") and _APP_INSTANCIA.root.winfo_exists():
        root = _APP_INSTANCIA.root
        
        # 1. Limpiar la interfaz
        for child in root.winfo_children():
            child.destroy()

        root.configure(bg="#1e1e1e")

        lang = _obtener_idioma_activo()
        t = TEXTOS.get(lang, TEXTOS["en"])

        # 2. Marco contenedor centrado
        frame_error = tk.Frame(root, bg="#2d2d2d", padx=30, pady=30, highlightbackground="#ff5555", highlightthickness=1)
        frame_error.place(relx=0.5, rely=0.5, anchor="center")

        lbl_titulo = tk.Label(frame_error, text=t["titulo"], font=("Sans", 14, "bold"), fg="#ffffff", bg="#2d2d2d")
        lbl_titulo.pack(pady=(0, 15))

        lbl_mensaje = tk.Label(
            frame_error, 
            text=t["cuerpo"], 
            justify="center", 
            wraplength=450, 
            fg="#cccccc", 
            bg="#2d2d2d",
            font=("Sans", 10)
        )
        lbl_mensaje.pack(pady=(0, 20))

        btn_reiniciar = tk.Button(
            frame_error, 
            text=t["boton"], 
            command=_reiniciar_aplicacion, 
            bg="#00ffcc", 
            fg="#000000",
            font=("Sans", 10, "bold"),
            padx=15,
            pady=5,
            relief="flat"
        )
        btn_reiniciar.pack()

def _atrapador_de_errores(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    lineas_error = traceback.format_exception(exc_type, exc_value, exc_traceback)
    texto_error = "".join(lineas_error)

    # 1. Envío silencioso e instantáneo a Telegram (Texto plano garantizado)
    try:
        mensaje = f"⚠️ REPORTE DE ERROR AUTOMÁTICO ⚠️\n\n{texto_error[-3500:]}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Enviamos sin parse_mode para evitar fallos de sintaxis por guiones bajos o símbolos
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": mensaje
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=4)
    except Exception as e:
        print(f"[Error envío Telegram]: {e}")

    # 2. Despliega la pantalla de aviso en la interfaz
    _mostrar_pantalla_error_en_app()

def activar_atrapador():
    """Activa la captura global para errores fuera del loop de Tkinter."""
    sys.excepthook = _atrapador_de_errores
