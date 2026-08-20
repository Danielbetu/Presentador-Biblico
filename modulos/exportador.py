import os
import time
import textwrap
import subprocess
import webbrowser
import shutil
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageDraw, ImageFont
from modulos.constantes import DIR_BASE, DIR_ASSETS_IMAGES, DICCIONARIO_UI


def copiar_imagen_al_portapapeles(ruta_imagen):
    try:
        comando = f"xclip -selection clipboard -t image/png -i '{ruta_imagen}'"
        subprocess.run(comando, shell=True, check=True)
        return True
    except Exception as e:
        print(f"[ERROR PORTAPAPELES]: {e}")
        return False


def abrir_destino_compartir(app, destino, win_compartir):
    # 1. Destruir la ventana de selección de compartir si existe
    if win_compartir and win_compartir.winfo_exists():
        win_compartir.destroy()

    # 2. Abrir el destino correspondiente en proceso independiente desacoplado
    if destino == "whatsapp":
        try:
            url = "https://web.whatsapp.com"
            if shutil.which("xdg-open"):
                subprocess.Popen(
                    ["xdg-open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            else:
                webbrowser.open(url)
        except Exception as e:
            print(f"[ERROR WA]: {e}")

    elif destino == "telegram":
        ejecutable_tg = shutil.which("telegram-desktop") or shutil.which("telegram")

        if ejecutable_tg:
            try:
                subprocess.Popen(
                    [ejecutable_tg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            except Exception as e:
                print(f"[ERROR EXEC TG]: {e}")
                webbrowser.open("https://web.telegram.org")
        else:
            messagebox.showwarning(
                "Telegram", 
                "No se detectó la aplicación nativa de Telegram instalada.\nSe abrirá la versión web."
            )
            try:
                url_tg = "https://web.telegram.org"
                if shutil.which("xdg-open"):
                    subprocess.Popen(
                        ["xdg-open", url_tg],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                else:
                    webbrowser.open(url_tg)
            except Exception as e:
                print(f"[ERROR TG WEB]: {e}")

    # 3. Cerrar la aplicación Presentador Bíblico de forma completamente limpia
    app.salir_app()


def mostrar_ventana_compartir(app, ruta_imagen):
    copiar_imagen_al_portapapeles(ruta_imagen)

    win_compartir = tk.Toplevel(app.root)
    win_compartir.overrideredirect(True)
    ancho_c, alto_c = 400, 230
    x = app.root.winfo_x() + (app.ancho_pantalla // 2) - (ancho_c // 2)
    y = app.root.winfo_y() + (app.alto_pantalla // 2) - (alto_c // 2)
    win_compartir.geometry(f"{ancho_c}x{alto_c}+{x}+{y}")
    win_compartir.configure(bg="#1e1e1e", highlightbackground="#00ffcc", highlightthickness=2)

    ui_strings = DICCIONARIO_UI.get(app.idioma_actual, DICCIONARIO_UI["es"])

    lbl_tit = tk.Label(win_compartir, text=ui_strings.get("compartir_tit", "COMPARTIR POSTAL"), bg="#1e1e1e", fg="#00ffcc", font=("Ubuntu", 12, "bold"))
    lbl_tit.pack(pady=(15, 5))

    lbl_sub = tk.Label(
        win_compartir, 
        text=ui_strings.get("compartir_msg", "¡Imagen copiada al portapapeles!\nSelecciona el destino y pega con Ctrl + V"), 
        bg="#1e1e1e", fg="#e0e0e0", font=("Ubuntu", 10), justify="center"
    )
    lbl_sub.pack(pady=5)

    marco_botones = tk.Frame(win_compartir, bg="#1e1e1e")
    marco_botones.pack(pady=15)

    path_wa = None
    for ext in ["Whatsapp.jpeg", "Whatsapp.jpg", "Whatsapp.png", "whatsapp.jpeg", "whatsapp.jpg", "whatsapp.png"]:
        p = os.path.join(DIR_ASSETS_IMAGES, ext)
        if os.path.exists(p):
            path_wa = p
            break

    path_tg = None
    for ext in ["Telegram.jpeg", "Telegram.jpg", "Telegram.png", "telegram.jpeg", "telegram.jpg", "telegram.png"]:
        p = os.path.join(DIR_ASSETS_IMAGES, ext)
        if os.path.exists(p):
            path_tg = p
            break

    icon_wa, icon_tg = None, None

    if path_wa:
        try:
            img_wa = Image.open(path_wa).resize((38, 38), Image.Resampling.LANCZOS)
            icon_wa = ImageTk.PhotoImage(img_wa)
        except Exception as e:
            print(f"[ERROR CARGA LOGO WA]: {e}")

    if path_tg:
        try:
            img_tg = Image.open(path_tg).resize((38, 38), Image.Resampling.LANCZOS)
            icon_tg = ImageTk.PhotoImage(img_tg)
        except Exception as e:
            print(f"[ERROR CARGA LOGO TG]: {e}")

    if icon_wa:
        btn_wa = tk.Button(
            marco_botones, image=icon_wa, bg="#1e1e1e", activebackground="#25D366",
            bd=0, relief="flat", cursor="hand2", command=lambda: abrir_destino_compartir(app, "whatsapp", win_compartir)
        )
        btn_wa.image = icon_wa
    else:
        btn_wa = tk.Button(
            marco_botones, text="WhatsApp", bg="#25D366", fg="white", font=("Ubuntu", 10, "bold"),
            bd=0, relief="flat", padx=12, pady=8, cursor="hand2", command=lambda: abrir_destino_compartir(app, "whatsapp", win_compartir)
        )
    btn_wa.pack(side="left", padx=25)

    if icon_tg:
        btn_tg = tk.Button(
            marco_botones, image=icon_tg, bg="#1e1e1e", activebackground="#0088CC",
            bd=0, relief="flat", cursor="hand2", command=lambda: abrir_destino_compartir(app, "telegram", win_compartir)
        )
        btn_tg.image = icon_tg
    else:
        btn_tg = tk.Button(
            marco_botones, text="Telegram", bg="#0088CC", fg="white", font=("Ubuntu", 10, "bold"),
            bd=0, relief="flat", padx=12, pady=8, cursor="hand2", command=lambda: abrir_destino_compartir(app, "telegram", win_compartir)
        )
    btn_tg.pack(side="left", padx=25)

    btn_cerrar = tk.Button(
        win_compartir, text=ui_strings.get("volver", "Volver").upper(), 
        bg="#333333", fg="white", font=("Ubuntu", 9, "bold"), bd=0, relief="flat", 
        padx=20, pady=4, cursor="hand2", command=win_compartir.destroy
    )
    btn_cerrar.pack(pady=(5, 5))


def exportar_postal_imagen(app):   
    try:
        if not hasattr(app, 'texto_versiculo_actual') or not app.texto_versiculo_actual:
            return

        app.destruir_menu_flotante()

        dir_export = os.path.join(DIR_BASE, "media", "exportadas")
        os.makedirs(dir_export, exist_ok=True)

        ancho, alto = 1920, 1080 
        if app.imagen_actual_path and os.path.exists(app.imagen_actual_path) and not app.modo_sin_paisaje:
            with Image.open(app.imagen_actual_path) as img_raw:
                base_img = img_raw.copy().resize((ancho, alto))
            base_img = ImageEnhance.Brightness(base_img).enhance(0.5)
        else:
            base_img = Image.new("RGB", (ancho, alto), color="#0e1116")

        draw = ImageDraw.Draw(base_img)

        try:
            font_v = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf", 55)
            font_c = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf", 40)
        except:
            try:
                font_v = ImageFont.truetype("DejaVuSans-Oblique.ttf", 55)
                font_c = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
            except:
                font_v = ImageFont.load_default()
                font_c = ImageFont.load_default()

        lineas = textwrap.wrap(app.texto_versiculo_actual, width=50)
        
        y_text = (alto // 2) - (len(lineas) * 35)
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font_v)
            w_line = bbox[2] - bbox[0]
            draw.text(((ancho - w_line) // 2, y_text), linea, fill="white", font=font_v)
            y_text += 70

        cita_str = f"— {app.cita_limpia_export.upper()}"
        bbox_c = draw.textbbox((0, 0), cita_str, font=font_c)
        w_c = bbox_c[2] - bbox_c[0]
        draw.text(((ancho - w_c) // 2, y_text + 60), cita_str, fill="#00ffcc", font=font_c)

        nombre_archivo = f"Postal_{app.idioma_actual.upper()}_{int(time.time())}.png"
        ruta_salida = os.path.join(dir_export, nombre_archivo)
        base_img.save(ruta_salida)

        mostrar_ventana_compartir(app, ruta_salida)

    except Exception as e:
        print(f"[ERROR EXPORTAR POSTAL]: {e}")
