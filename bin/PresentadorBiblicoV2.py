#!/usr/bin/env python3
import os
import sys
import random
import json
import subprocess
import tkinter as tk

# Asegurar que Python encuentre la carpeta de módulos sin importar dónde estés parado
Directorio_Raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if Directorio_Raiz not in sys.path:
    sys.path.insert(0, Directorio_Raiz)

# Ruta a la fuente Lora Regular
ruta_fuente_lora = os.path.join(Directorio_Raiz, "assets", "Lora-VariableFont_wght.ttf")

# Ahora importamos el módulo del atrapador
from modulos.atrapador import activar_atrapador

activar_atrapador()

from PIL import Image, ImageTk, ImageEnhance

# Añadir raíz del proyecto al sys.path
DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIR_RAIZ not in sys.path:
    sys.path.insert(0, DIR_RAIZ)

from modulos.constantes import *
from modulos.audio import reproducir_versiculo_async
from modulos.exportador import exportar_postal_imagen
from modulos.buscador import BuscadorInteligente
from modulos.lector import LectorBiblico
from modulos.bienvenida import verificar_y_mostrar_bienvenida


class PresentadorBiblico:
    def __init__(self, root):
        self.root = root
        self.root.tk.call('tk', 'scaling', 1.0)
        self.root.overrideredirect(True)
        
        ancho_maximo = self.root.winfo_screenwidth()
        alto_maximo = self.root.winfo_screenheight()
        
        self.ancho_pantalla = int(ancho_maximo * 0.70)
        self.alto_pantalla = int(alto_maximo * 0.70)
        
        pos_x = (ancho_maximo - self.ancho_pantalla) // 2
        pos_y = (alto_maximo - self.alto_pantalla) // 2
        
        self.root.geometry(f"{self.ancho_pantalla}x{self.alto_pantalla}+{pos_x}+{pos_y}")
        self.root.configure(bg="#121212")
        
        self.primer_arranque = True # Estado por defecto
        
        self.audio_process = None
        self.audio_active = False
        self.pista_actual_idx = 0
        
        self.paisaje_fijado = False
        self.modo_sin_paisaje = False
        self.modo_cebra = True 
        
        self.tamano_fuente_lector = 15
        self.win_menu = None
        self.win_busca = None
        self.ventana_lectura = None
        
        self.canvas = tk.Canvas(self.root, width=self.ancho_pantalla, height=self.alto_pantalla, bd=0, highlightthickness=0, bg="#121212")
        self.canvas.pack(fill="both", expand=True)
        
        self.idioma_actual = "es"
        self.libro_actual_lector = "GÉNESIS"
        self.capitulo_actual_lector = "1"
        self.imagen_actual_path = None
        
        self.cargar_configuracion()
        
        self.favoritos_db = self.leer_favoritos_json()
        self.lista_citas = list(self.favoritos_db.keys())
        self.lista_citas = [c for c in self.lista_citas if ":" in c and not c.lower().startswith("aquí") and not c.lower().startswith("esta")]
        
        self.indice = random.randint(0, len(self.lista_citas) - 1) if self.lista_citas else 0
        self.historial = [self.indice]
        self.pos_historial = 0
        
        self.fondo = None
        self.texto_versiculo_actual = ""
        self.fotos_validas = []
        self.cargar_lista_fotos_validas()
        
        self.root.bind("<Left>", lambda e: self.cambiar_texto(-1))
        self.root.bind("<Right>", lambda e: self.cambiar_texto(1))
        self.root.bind("<space>", lambda e: self.reproducir_lectura_actual())
        
        self.mostrar_pantalla_carga()
        verificar_y_mostrar_bienvenida(self)

    def destruir_menu_flotante(self):
        if hasattr(self, 'win_menu') and self.win_menu and self.win_menu.winfo_exists():
            try:
                self.win_menu.destroy()
            except Exception:
                pass
            self.win_menu = None

    def cargar_lista_fotos_validas(self):
        if os.path.exists(DIR_ASSETS_IMAGES):
            todas_las_fotos = [f for f in os.listdir(DIR_ASSETS_IMAGES) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.avif'))]
            for f in todas_las_fotos:
                ruta = os.path.join(DIR_ASSETS_IMAGES, f)
                try:
                    with Image.open(ruta) as img:
                        ancho, alto = img.size
                        if ancho >= self.ancho_pantalla and alto >= self.alto_pantalla:
                            self.fotos_validas.append(ruta)
                except:
                    pass
        if not self.fotos_validas and os.path.exists(DIR_ASSETS_IMAGES):
            self.fotos_validas = [os.path.join(DIR_ASSETS_IMAGES, f) for f in os.listdir(DIR_ASSETS_IMAGES) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.avif'))]

    def cargar_configuracion(self):
        if os.path.exists(PATH_CONFIG_JSON):
            try:
                with open(PATH_CONFIG_JSON, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    idioma_guardado = config.get("idioma")
                    if idioma_guardado in ["es", "en", "fr", "it", "por"]:
                        self.idioma_actual = idioma_guardado
                    
                    ultimo_libro = config.get("ultimo_libro")
                    if ultimo_libro: self.libro_actual_lector = ultimo_libro
                    
                    ultimo_cap = config.get("ultimo_capitulo")
                    if ultimo_cap: self.capitulo_actual_lector = str(ultimo_cap)

                    self.modo_cebra = config.get("modo_cebra", True)
                    self.paisaje_fijado = config.get("paisaje_fijado", False)
                    self.modo_sin_paisaje = config.get("modo_sin_paisaje", False)
                    self.primer_arranque = config.get("primer_arranque", True)
                    
                    img_fijada = config.get("imagen_fijada_path")
                    if img_fijada and os.path.exists(img_fijada):
                        self.imagen_actual_path = img_fijada
            except:
                pass

    def guardar_configuracion(self):
        try:
            os.makedirs(DIR_DATA, exist_ok=True)
            datos = {
                "idioma": self.idioma_actual,
                "ultimo_libro": self.libro_actual_lector,
                "ultimo_capitulo": self.capitulo_actual_lector,
                "modo_cebra": self.modo_cebra,
                "paisaje_fijado": self.paisaje_fijado,
                "modo_sin_paisaje": self.modo_sin_paisaje,
                "imagen_fijada_path": self.imagen_actual_path if self.paisaje_fijado else None,
                "primer_arranque": self.primer_arranque
            }
            with open(PATH_CONFIG_JSON, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[ERROR CONFIG]: {e}")

    def leer_favoritos_json(self):
        path_json = os.path.join(DIR_DATA, "versiculos_favoritos_multilenguaje.json")
        if os.path.exists(path_json):
            try:
                with open(path_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def mostrar_pantalla_carga(self):
        self.canvas.delete("all")
        self.root.update_idletasks()
        
        ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])
        nombre_splash = ui_strings.get("splash_file", "Presentador_Bíblico_ES.jpg")
        
        path_splash = os.path.join(DIR_ASSETS, nombre_splash)
        
        # Búsqueda alternativa de respaldo si el nombre no coincide exacto
        if not os.path.exists(path_splash) and os.path.exists(DIR_ASSETS):
            archivos = [f for f in os.listdir(DIR_ASSETS) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if archivos:
                path_splash = os.path.join(DIR_ASSETS, archivos[0])

        if os.path.exists(path_splash):
            try:
                with Image.open(path_splash) as img_raw:
                    img_splash = img_raw.copy().resize((self.ancho_pantalla, self.alto_pantalla))
                self.fondo_splash = ImageTk.PhotoImage(img_splash)
                self.canvas.create_image(0, 0, image=self.fondo_splash, anchor="nw")
            except Exception as e:
                print(f"[ERROR SPLASH]: {e}")
                self.canvas.create_text(self.ancho_pantalla // 2, self.alto_pantalla // 2, text="...", fill="#00ffcc", font=("Ubuntu", 24, "bold"))
        else:
            self.canvas.create_text(self.ancho_pantalla // 2, self.alto_pantalla // 2, text="...", fill="#00ffcc", font=("Ubuntu", 24, "bold"))
        
        self.root.update()
        # 2800 ms (2.8 segundos) para apreciar bien la placa
        self.root.after(2800, self.actualizar_interfaz)

    def actualizar_interfaz(self):    
        self.canvas.delete("all")
        centro_x = self.ancho_pantalla // 2
        centro_y = self.alto_pantalla // 2
        
        if self.modo_sin_paisaje:
            self.canvas.configure(bg="#0e1116")
        else:
            self.canvas.configure(bg="#121212")
            if not self.imagen_actual_path and self.fotos_validas:
                self.imagen_actual_path = random.choice(self.fotos_validas)
            
            if self.imagen_actual_path and os.path.exists(self.imagen_actual_path):
                try:
                    with Image.open(self.imagen_actual_path) as img_raw:
                        img_resized = img_raw.copy().resize((self.ancho_pantalla, self.alto_pantalla))
                    self.fondo = ImageTk.PhotoImage(ImageEnhance.Brightness(img_resized).enhance(0.5))
                    self.canvas.create_image(0, 0, image=self.fondo, anchor="nw")
                except:
                    pass
        
        ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])
        
        titulo_texto = ui_strings.get("titulo_ventana", "VERSÍCULO DEL DÍA").upper()
        menu_texto = ui_strings.get("trigger_menu", "MENÚ")
        
        self.canvas.create_text(centro_x, 40, text=titulo_texto, fill="#EAD2AC", font=("Ubuntu", 14, "bold"))
        self.btn_menu_trigger = self.canvas.create_text(60, 40, text=menu_texto, fill="#F2E8DA", font=("Ubuntu", 11, "bold"))
        self.canvas.tag_bind(self.btn_menu_trigger, "<Button-1>", self.mostrar_menu_flotante)
        
        btn_close = self.canvas.create_text(self.ancho_pantalla - 40, 40, text="✕", fill="#ffffff", font=("Ubuntu", 20, "bold"))
        self.canvas.tag_bind(btn_close, "<Button-1>", lambda e: self.salir_app())
        
        if self.lista_citas:
            cita_base_esp = self.lista_citas[self.indice]
            self.texto_versiculo_actual = ""
            cita_final = cita_base_esp
            
            if self.idioma_actual == "es":
                datos_cita = self.favoritos_db.get(cita_base_esp, {})
                self.texto_versiculo_actual = datos_cita.get("es", "")
                cita_final = cita_base_esp.replace("RVR1960", "").replace("RVR 1960", "").strip()
            else:
                path_txt_fav = os.path.join(DIR_DATA, f"Versiculos_biblicos_favoritos_{self.idioma_actual.upper()}.txt")
                if os.path.exists(path_txt_fav):
                    try:
                        with open(path_txt_fav, 'r', encoding='utf-8') as f:
                            bloques = f.read().split('\n\n')
                            if self.indice < len(bloques):
                                lineas_bloque = [l.strip() for l in bloques[self.indice].split('\n') if l.strip()]
                                if len(lineas_bloque) >= 2:
                                    self.texto_versiculo_actual = lineas_bloque[0]
                                    cita_final = lineas_bloque[1]
                    except:
                        pass
            
            if not self.texto_versiculo_actual:
                datos_cita = self.favoritos_db.get(cita_base_esp, {})
                self.texto_versiculo_actual = datos_cita.get(self.idioma_actual, "")
                cita_final = cita_base_esp

            cita_limpia = cita_final.replace("RVR1960", "").replace("RVR 1960", "").replace("KJV", "").strip()
            self.cita_limpia_export = cita_limpia 
            
            ancho_texto_relativo = int(self.ancho_pantalla * 0.85)
            
            self.canvas.create_text(centro_x, centro_y - 20, text=self.texto_versiculo_actual, fill="white", font=("Ubuntu", 20, "italic"), width=ancho_texto_relativo, justify="center")
            self.canvas.create_text(centro_x, self.alto_pantalla - 160, text=f"— {cita_limpia.upper()}", fill="#ffffff", font=("Ubuntu", 14, "bold"))
            
            self.btn_read = self.canvas.create_text(centro_x - 110, self.alto_pantalla - 120, text=ui_strings.get("leer_entero", "Leer capítulo entero"), fill="#00ffcc", font=("Ubuntu", 11, "underline"))
            self.canvas.tag_bind(self.btn_read, "<Button-1>", lambda e: self.abrir_capitulo_completo())

            self.btn_quick_bg = self.canvas.create_text(centro_x + 110, self.alto_pantalla - 120, text=ui_strings.get("btn_cambiar_fondo", "🖼️ Cambiar paisaje"), fill="#EAD2AC", font=("Ubuntu", 11, "bold"))
            self.canvas.tag_bind(self.btn_quick_bg, "<Button-1>", lambda e: self.cambiar_paisaje())
        
        self.btn_ant = self.canvas.create_text(centro_x - 150, self.alto_pantalla - 60, text=ui_strings.get("btn_anterior", "◄ Anterior"), fill="#2196F3", font=("Ubuntu", 11, "bold"))
        self.canvas.tag_bind(self.btn_ant, "<Button-1>", lambda e: self.cambiar_texto(-1))
        self.btn_sig = self.canvas.create_text(centro_x + 150, self.alto_pantalla - 60, text=ui_strings.get("btn_siguiente", "Nuevo ►"), fill="#2196F3", font=("Ubuntu", 11, "bold"))
        self.canvas.tag_bind(self.btn_sig, "<Button-1>", lambda e: self.cambiar_texto(1))
        
        self.btn_audio_icon = self.canvas.create_text(self.ancho_pantalla - 40, self.alto_pantalla - 40, text="🔊", fill="#00ffcc", font=("Ubuntu", 22))
        self.canvas.tag_bind(self.btn_audio_icon, "<Button-1>", lambda e: self.reproducir_lectura_actual())

    def reproducir_lectura_actual(self):
        if hasattr(self, 'texto_versiculo_actual') and self.texto_versiculo_actual:
            reproducir_versiculo_async(self.texto_versiculo_actual, self.idioma_actual)

    def cambiar_texto(self, dir):
        if not self.lista_citas: return
        if dir == 1:
            nuevo_indice = random.randint(0, len(self.lista_citas) - 1)
            if self.pos_historial < len(self.historial) - 1:
                self.historial = self.historial[:self.pos_historial + 1]
            self.historial.append(nuevo_indice)
            self.pos_historial += 1
            self.indice = nuevo_indice
        elif dir == -1:
            if self.pos_historial > 0:
                self.pos_historial -= 1
                self.indice = self.historial[self.pos_historial]
        
        if not self.paisaje_fijado:
            self.imagen_actual_path = None
        self.actualizar_interfaz()

    def cambiar_paisaje(self):
        self.destruir_menu_flotante()
        self.paisaje_fijado = False
        self.modo_sin_paisaje = False
        if self.fotos_validas:
            nueva_foto = random.choice(self.fotos_validas)
            while len(self.fotos_validas) > 1 and nueva_foto == self.imagen_actual_path:
                nueva_foto = random.choice(self.fotos_validas)
            self.imagen_actual_path = nueva_foto
            self.actualizar_interfaz()
        self.guardar_configuracion()

    def mantener_paisaje_actual(self):
        self.destruir_menu_flotante()
        self.paisaje_fijado = True
        self.modo_sin_paisaje = False
        self.guardar_configuracion()

    def activar_sin_paisaje(self):
        self.destruir_menu_flotante()
        self.modo_sin_paisaje = True
        self.paisaje_fijado = False
        self.guardar_configuracion()
        self.actualizar_interfaz()
        
    def solicitar_confirmacion_borrado(self):
        """Muestra dentro del menú flotante la pantalla de confirmación en rojo."""
        if hasattr(self, 'win_menu') and self.win_menu and self.win_menu.winfo_exists():
            for widget in self.win_menu.winfo_children():
                widget.destroy()

            ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])

            # Título Rojo
            lbl_tit = tk.Label(
                self.win_menu, 
                text=ui_strings.get("conf_borrar_tit", "CONFIRMAR ELIMINACIÓN"), 
                bg="#1e1e1e", fg="#ff4444", font=("Ubuntu", 10, "bold")
            )
            lbl_tit.pack(pady=(15, 10))

            # Mensaje explicativo
            lbl_msg = tk.Label(
                self.win_menu, 
                text=ui_strings.get("conf_borrar_msg", "¿Querés borrar la imagen?"), 
                bg="#1e1e1e", fg="white", font=("Ubuntu", 9, "bold"),
                justify="center", wraplength=280
            )
            lbl_msg.pack(pady=(0, 15), padx=10)

            # Botón SÍ, BORRAR (Rojo)
            btn_si = tk.Button(
                self.win_menu,
                text=ui_strings.get("btn_si_borrar", "SÍ, BORRAR"),
                bg="#ff4444", fg="white", font=("Ubuntu", 10, "bold"),
                activebackground="#d32f2f", activeforeground="white",
                bd=0, relief="flat", cursor="hand2", pady=6,
                command=self.ejecutar_borrado_confirmado
            )
            btn_si.pack(fill="x", padx=15, pady=4)

            # Botón CANCELAR (Gris con borde)
            btn_no = tk.Button(
                self.win_menu,
                text=ui_strings.get("btn_cancelar", "CANCELAR"),
                bg="#333333", fg="white", font=("Ubuntu", 10, "bold"),
                activebackground="#444444", activeforeground="white",
                bd=1, relief="solid", cursor="hand2", pady=6,
                command=self.mostrar_subsubmenu_paisajes
            )
            btn_no.pack(fill="x", padx=15, pady=(4, 15))

            self.win_menu.update_idletasks()
            alto_real = self.win_menu.winfo_reqheight()
            self.win_menu.geometry(f"320x{alto_real}")

    def ejecutar_borrado_confirmado(self):
        """Se ejecuta únicamente cuando el usuario presiona 'SÍ, BORRAR'."""
        self.destruir_menu_flotante()
        if self.imagen_actual_path and os.path.exists(self.imagen_actual_path):
            try:
                archivo_a_borrar = self.imagen_actual_path
                if archivo_a_borrar in self.fotos_validas:
                    self.fotos_validas.remove(archivo_a_borrar)
                
                os.remove(archivo_a_borrar)
                self.imagen_actual_path = None
                self.cambiar_paisaje()
            except Exception as e:
                print(f"[ERROR BORRAR PAISAJE]: {e}")

    def mostrar_subsubmenu_paisajes(self):
        if hasattr(self, 'win_menu') and self.win_menu.winfo_exists():
            for widget in self.win_menu.winfo_children():
                widget.destroy()

            ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])

            opciones_paisaje = [
                (ui_strings.get("paisaje_cambiar", "Cambiar paisaje ahora"), self.cambiar_paisaje),
                (ui_strings.get("paisaje_mantener", "Mantener paisaje actual"), self.mantener_paisaje_actual),
                (ui_strings.get("paisaje_sin", "Pantalla sin paisaje"), self.activar_sin_paisaje),
                (ui_strings.get("paisaje_borrar", "🗑️ Borrar este paisaje de la galería"), self.solicitar_confirmacion_borrado),
                (ui_strings.get("volver", "Volver"), self.mostrar_menu_principal_contenido)
            ]

            lbl_sub_tit = tk.Label(self.win_menu, text=ui_strings.get("opciones_paisaje", "Opciones de paisaje"), bg="#1e1e1e", fg="#00ffcc", font=("Ubuntu", 10, "bold"), anchor="w", padx=15)
            lbl_sub_tit.pack(pady=(15, 10), fill="x")

            for t, cmd in opciones_paisaje:
                lbl = tk.Label(self.win_menu, text=t, bg="#1e1e1e", fg="white", font=("Ubuntu", 11), cursor="hand2", anchor="w", padx=15)
                lbl.pack(pady=4, fill="x")
                lbl.bind("<Button-1>", lambda e, c=cmd: c())

            self.win_menu.update_idletasks()
            alto_real = self.win_menu.winfo_reqheight() + 15
            self.win_menu.geometry(f"320x{alto_real}")

    def mostrar_subsubmenu_idiomas(self):
        if hasattr(self, 'win_menu') and self.win_menu is not None and self.win_menu.winfo_exists():
            for widget in self.win_menu.winfo_children():
                widget.destroy()

            ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])

            opciones_idioma = [
                ("ESPAÑOL", lambda: self.cambiar_idioma("es")),
                ("ENGLISH", lambda: self.cambiar_idioma("en")),
                ("FRANÇAIS", lambda: self.cambiar_idioma("fr")),
                ("ITALIANO", lambda: self.cambiar_idioma("it")),
                ("PORTUGUÊS", lambda: self.cambiar_idioma("por")),
                (ui_strings.get("volver", "Volver"), self.mostrar_menu_principal_contenido)
            ]

            lbl_sub_tit = tk.Label(self.win_menu, text=ui_strings.get("cambiar_idioma", "Cambiar idioma"), bg="#1e1e1e", fg="#00ffcc", font=("Ubuntu", 10, "bold"), anchor="w", padx=15)
            lbl_sub_tit.pack(pady=(15, 10), fill="x")

            mapa_lang = {"es": "ESPAÑOL", "en": "ENGLISH", "fr": "FRANÇAIS", "it": "ITALIANO", "por": "PORTUGUÊS"}

            for t, cmd in opciones_idioma:
                prefijo = "• " if (t in mapa_lang.values() and mapa_lang.get(self.idioma_actual) == t) else ""
                lbl = tk.Label(self.win_menu, text=f"{prefijo}{t}", bg="#1e1e1e", fg="white", font=("Ubuntu", 11), cursor="hand2", anchor="w", padx=15)
                lbl.pack(pady=4, fill="x")
                lbl.bind("<Button-1>", lambda e, c=cmd: c())

            self.win_menu.update_idletasks()
            alto_real = self.win_menu.winfo_reqheight() + 15
            self.win_menu.geometry(f"320x{alto_real}")

    def mostrar_menu_principal_contenido(self):
        if hasattr(self, 'win_menu') and self.win_menu.winfo_exists():
            for widget in self.win_menu.winfo_children():
                widget.destroy()

            ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])
            texto_musica = ui_strings.get("menu_musica_off" if self.audio_active else "menu_musica_on", "🔊 Música")

            grupos_opciones = [
                [
                    (texto_musica, self.alternar_musica, "white"),
                    (ui_strings.get("menu_paisaje", "🖼️ Opciones de paisaje"), self.mostrar_subsubmenu_paisajes, "white"),
                    (ui_strings.get("menu_exportar", "✉️ Compartir postal (WhatsApp / Telegram)"), lambda: exportar_postal_imagen(self), "#00ffcc"),
                ],
                [
                    (ui_strings.get("menu_buscador", "🔍 Buscador de frases"), lambda: BuscadorInteligente(self), "white"),
                    (ui_strings.get("menu_leer_biblia", "📖 Leer la Biblia entera"), lambda: LectorBiblico(self), "white"),
                ],
                [
                    (ui_strings.get("menu_idioma", "🌐 Cambiar idioma"), self.mostrar_subsubmenu_idiomas, "white"),
                    (ui_strings.get("menu_sabias_que", "💡 ¿Sabías que...?"), self.mostrar_sabias_que, "#f4d03f"),
                    (ui_strings.get("menu_info", "ℹ️ Información sobre la app"), self.mostrar_info, "#cccccc"),
                    (ui_strings.get("btn_salir", "✕ Salir de la app"), self.salir_app, "#ff5555"),
                ]
            ]

            def al_entrar(lbl):
                lbl.config(bg="#2a2a2a")

            def al_salir(lbl):
                lbl.config(bg="#1e1e1e")

            for idx_grupo, grupo in enumerate(grupos_opciones):
                if idx_grupo > 0:
                    sep = tk.Frame(self.win_menu, bg="#333333", height=1)
                    sep.pack(fill="x", padx=10, pady=4)

                for t, cmd, color in grupo:
                    lbl = tk.Label(
                        self.win_menu, text=t, bg="#1e1e1e", fg=color, 
                        font=("Ubuntu", 10, "bold" if color != "white" else "normal"), 
                        cursor="hand2", anchor="w", padx=15, pady=3
                    )
                    lbl.pack(fill="x")
                    lbl.bind("<Enter>", lambda e, l=lbl: al_entrar(l))
                    lbl.bind("<Leave>", lambda e, l=lbl: al_salir(l))
                    lbl.bind("<Button-1>", lambda e, c=cmd: self.ejecutar_comando_menu(c))

            self.win_menu.update_idletasks()
            alto_real = self.win_menu.winfo_reqheight() + 10
            self.win_menu.geometry(f"320x{alto_real}")

    def mostrar_menu_flotante(self, event, origen_lectura=False):
        self.win_menu = tk.Toplevel(self.root)
        self.win_menu.overrideredirect(True)
        self.win_menu.configure(bg="#1e1e1e", highlightbackground="#444", highlightthickness=1)
        
        ancho_menu = 320
        if origen_lectura:
            self.win_menu.geometry(f"{ancho_menu}x1+40+70")
        else:
            self.win_menu.geometry(f"{ancho_menu}x1+{self.root.winfo_x()+40}+{self.root.winfo_y()+60}")
            
        self.mostrar_menu_principal_contenido()
        self.win_menu.bind("<FocusOut>", lambda e: self.destruir_menu_flotante())
        self.win_menu.focus_set()

    def ejecutar_comando_menu(self, cmd):
        if cmd not in [self.mostrar_subsubmenu_paisajes, self.mostrar_subsubmenu_idiomas]:
            self.destruir_menu_flotante()
        cmd()

    def abrir_capitulo_completo(self):
      """Parsea la cita del versículo actual y abre el lector en el libro y capítulo correctos."""
      if hasattr(self, 'cita_limpia_export') and self.cita_limpia_export:
        try:
          import re

          # Extraer libro y capítulo de la cita (ej. "Efesios 3:16-19" -> "EFESIOS", "3")
          match = re.search(r'^(.*?)\s+(\d+)[:\.]', self.cita_limpia_export)
          if match:
            nombre_libro = match.group(1).strip().upper()
            capitulo_num = match.group(2).strip()

            self.libro_actual_lector = nombre_libro
            self.capitulo_actual_lector = capitulo_num
            self.guardar_configuracion()
        except Exception as e:
          print(f'[ERROR PARSER CITA LECTOR]: {e}')

      LectorBiblico(self)

    def cambiar_idioma(self, nuevo_idioma):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.idioma_actual = nuevo_idioma
        self.guardar_configuracion()
        self.destruir_menu_flotante()
        self.actualizar_interfaz()
        self.root.geometry(f"{self.ancho_pantalla}x{self.alto_pantalla}+{x}+{y}")

    def mostrar_info(self):
        win_info = tk.Toplevel(self.root)
        win_info.overrideredirect(True)
    
        # Aumentamos el ancho a 520 px (y el alto a 200 px por si hace salto de línea)
        ancho_info, alto_info = 520, 200
        x = self.root.winfo_x() + (self.ancho_pantalla // 2) - (ancho_info // 2)
        y = self.root.winfo_y() + (self.alto_pantalla // 2) - (alto_info // 2)
        win_info.geometry(f"{ancho_info}x{alto_info}+{x}+{y}")
        win_info.configure(bg="#1e1e1e", highlightbackground="#444", highlightthickness=1)
    
        ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])
        tk.Label(win_info, text=ui_strings.get("info_tit", "PRESENTADOR BÍBLICO"), bg="#1e1e1e", fg="#00ffcc", font=("Ubuntu", 12, "bold")).pack(pady=(20, 5))
    
        # Agregamos wraplength=480 para que envuelva el texto si es necesario
        tk.Label(win_info, text=ui_strings.get("info_body", "Información de la app"), bg="#1e1e1e", fg="white", font=("Ubuntu", 11), justify="center", wraplength=480).pack(pady=10)
    
        tk.Button(win_info, text=ui_strings.get("btn_aceptar", "Aceptar"), bg="#333333", fg="white", font=("Ubuntu", 10, "bold"), activebackground="#444", activeforeground="white", bd=0, relief="flat", padx=25, pady=6, cursor="hand2", command=win_info.destroy).pack(pady=(5, 10))

    def mostrar_sabias_que(self):
        win_sabias = tk.Toplevel(self.root)
        win_sabias.overrideredirect(True)
        ancho_info, alto_info = 580, 430
        x = self.root.winfo_x() + (self.ancho_pantalla // 2) - (ancho_info // 2)
        y = self.root.winfo_y() + (self.alto_pantalla // 2) - (alto_info // 2)
        win_sabias.geometry(f"{ancho_info}x{alto_info}+{x}+{y}")
        win_sabias.configure(bg="#1e1e1e", highlightbackground="#f4d03f", highlightthickness=2)
        
        ui_strings = DICCIONARIO_UI.get(self.idioma_actual, DICCIONARIO_UI["es"])
        tk.Label(win_sabias, text=ui_strings.get("sabias_que_tit", "💡 ¿SABÍAS QUE...?"), bg="#1e1e1e", fg="#f4d03f", font=("Ubuntu", 14, "bold")).pack(pady=(20, 10))
        tk.Label(win_sabias, text=ui_strings.get("sabias_que_body", ""), bg="#1e1e1e", fg="white", font=("Ubuntu", 11), justify="left", wraplength=500).pack(padx=20, pady=10)
        tk.Button(win_sabias, text=ui_strings.get("btn_aceptar", "Aceptar"), bg="#f4d03f", fg="black", font=("Ubuntu", 10, "bold"), activebackground="#e5c100", activeforeground="black", bd=0, relief="flat", padx=25, pady=6, cursor="hand2", command=win_sabias.destroy).pack(pady=(10, 10))

    def alternar_musica(self):
        if self.audio_active: self.detener_musica()
        else: self.iniciar_musica()
        self.destruir_menu_flotante()

    def iniciar_musica(self):
        dir_audio = os.path.join(DIR_BASE, "media", "audio")
        if os.path.exists(dir_audio):
            pistas = sorted([f for f in os.listdir(dir_audio) if f.lower().endswith(('.mp3', '.wav'))])
            if pistas:
                if self.pista_actual_idx >= len(pistas): self.pista_actual_idx = 0
                pista_path = os.path.join(dir_audio, pistas[self.pista_actual_idx])
                try:
                    comando = ["ffplay", "-nodisp", "-loop", "0", "-af", "volume=0.4", pista_path]
                    self.audio_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.audio_active = True
                    self.pista_actual_idx = (self.pista_actual_idx + 1) % len(pistas)
                    self.actualizar_interfaz()
                except Exception as e:
                    print(f"[ERROR AUDIO]: {e}")

    def detener_musica(self):
        if hasattr(self, 'audio_process') and self.audio_process:
            try:
                self.audio_process.terminate()
                self.audio_process.wait(timeout=0.2)
            except Exception:
                try:
                    self.audio_process.kill()
                except Exception:
                    pass
            self.audio_process = None
        self.audio_active = False
        
    def borrar_paisaje_actual(self):
        """Elimina el archivo del paisaje actual del disco y cambia a uno nuevo."""
        if self.imagen_actual_path and os.path.exists(self.imagen_actual_path):
            try:
                archivo_a_borrar = self.imagen_actual_path
                # Si estaba en la lista de válidas, lo quitamos
                if archivo_a_borrar in self.fotos_validas:
                    self.fotos_validas.remove(archivo_a_borrar)
                
                # Borramos el archivo físico
                os.remove(archivo_a_borrar)
                self.imagen_actual_path = None
                
                # Cargamos un nuevo paisaje de inmediato
                self.cambiar_paisaje()
            except Exception as e:
                print(f"[ERROR BORRAR PAISAJE]: {e}")

    def salir_app(self):
        self.detener_musica()
        self.destruir_menu_flotante()
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.delete("all")
        self.fondo = None
        self.fondo_splash = None
        self.root.destroy()


if __name__ == "__main__":
  root = tk.Tk()

  app = PresentadorBiblico(root)

  from modulos.atrapador import asociar_a_app

  asociar_a_app(app)

  root.mainloop()
