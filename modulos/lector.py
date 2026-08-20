import os
import re
import textwrap
import unicodedata
import tkinter as tk
from tkinter import scrolledtext
from modulos.constantes import DIR_DATA, DICCIONARIO_UI, LIBROS_BIBLIA, CAPITULOS_POR_LIBRO, NOMBRES_BIBLIAS


class LectorBiblico:
    def __init__(self, app):
        self.app = app
        self.app.destruir_menu_flotante()
        self.cargar_y_renderizar_capitulo()

    def cambiar_tamano_fuente(self, delta):
        nuevo_tamano = self.app.tamano_fuente_lector + delta
        if 10 <= nuevo_tamano <= 30:
            self.app.tamano_fuente_lector = nuevo_tamano
            if hasattr(self, 'txt_area_lector') and self.txt_area_lector:
                self.txt_area_lector.config(font=("Ubuntu", self.app.tamano_fuente_lector))

    def alternar_modo_lectura(self):
        self.app.modo_cebra = not self.app.modo_cebra
        ui_strings = DICCIONARIO_UI.get(self.app.idioma_actual, DICCIONARIO_UI["es"])
        texto_btn = ui_strings.get(
            "btn_renglones_si" if self.app.modo_cebra else "btn_renglones_no", 
            "Renglones: ☑ Sí" if self.app.modo_cebra else "Renglones: ☐ No"
        )
        
        if hasattr(self, 'btn_cebra_toggle') and self.btn_cebra_toggle:
            self.btn_cebra_toggle.config(text=texto_btn)
            
        self.app.guardar_configuracion()
        self.cargar_y_renderizar_capitulo()

    def cambiar_capitulo_lector(self, delta):
        try:
            cap_actual = int(self.app.capitulo_actual_lector)
            lista_libros = LIBROS_BIBLIA.get(self.app.idioma_actual, LIBROS_BIBLIA["es"])
            idx_libro = lista_libros.index(self.app.libro_actual_lector)
            max_caps = CAPITULOS_POR_LIBRO[idx_libro]
            
            nuevo_cap = cap_actual + delta
            
            if nuevo_cap > max_caps:
                idx_libro = (idx_libro + 1) % len(lista_libros)
                self.app.libro_actual_lector = lista_libros[idx_libro]
                self.app.capitulo_actual_lector = "1"
            elif nuevo_cap < 1:
                idx_libro = (idx_libro - 1) % len(lista_libros)
                self.app.libro_actual_lector = lista_libros[idx_libro]
                max_caps_anterior = CAPITULOS_POR_LIBRO[idx_libro]
                self.app.capitulo_actual_lector = str(max_caps_anterior)
            else:
                self.app.capitulo_actual_lector = str(nuevo_cap)

            if hasattr(self, 'btn_libro') and self.btn_libro:
                self.btn_libro.config(text=self.app.libro_actual_lector)
            if hasattr(self, 'btn_cap') and self.btn_cap:
                self.btn_cap.config(text=self.app.capitulo_actual_lector)

            self.app.guardar_configuracion()
            self.cargar_y_renderizar_capitulo()
        except:
            pass

    def mostrar_vista_libros(self):
        self.marco_texto.pack_forget()
        self.marco_capitulos.pack_forget()
        self.marco_libros.pack(fill="both", expand=True, padx=80, pady=(30, 10))
        self.btn_libro.config(bg="#3a506b", fg="white")
        self.btn_cap.config(bg="#1b202e", fg="#f6f1e5")

    def mostrar_vista_capitulos(self):
        for widget in self.marco_capitulos.winfo_children():
            widget.destroy()
        
        try:
            indice_libro = LIBROS_BIBLIA[self.app.idioma_actual].index(self.app.libro_actual_lector)
            max_caps = CAPITULOS_POR_LIBRO[indice_libro]
        except:
            max_caps = 150

        for i in range(1, max_caps + 1):
            btn = tk.Button(self.marco_capitulos, text=str(i), bg="#141923", fg="#00ffcc", font=("Ubuntu", 14, "bold"), bd=1, relief="solid", activebackground="#3a506b", cursor="hand2", command=lambda c=i: self.ejecutar_seleccion_capitulo(c))
            btn.grid(row=(i-1)//10, column=(i-1)%10, sticky="nsew", padx=2, pady=2)
            self.marco_capitulos.grid_columnconfigure((i-1)%10, weight=1)

        self.marco_texto.pack_forget()
        self.marco_libros.pack_forget()
        self.marco_capitulos.pack(fill="both", expand=True, padx=120, pady=(30, 10))
        self.btn_libro.config(bg="#1b202e", fg="#f6f1e5")
        self.btn_cap.config(bg="#3a506b", fg="white")

    def ejecutar_seleccion_libro(self, libro_elegido):
        self.app.libro_actual_lector = libro_elegido
        self.btn_libro.config(text=libro_elegido)
        self.mostrar_vista_capitulos()

    def ejecutar_seleccion_capitulo(self, capitulo_elegido):
        self.app.capitulo_actual_lector = str(capitulo_elegido)
        self.app.guardar_configuracion()
        self.cargar_y_renderizar_capitulo()

    def mostrar_vista_texto(self):
        self.marco_libros.pack_forget()
        self.marco_capitulos.pack_forget()
        self.marco_texto.pack(fill="both", expand=True, padx=120, pady=(0, 10))
        self.btn_libro.config(bg="#1b202e", fg="#f6f1e5")
        self.btn_cap.config(bg="#1b202e", fg="#f6f1e5")

    def cargar_y_renderizar_capitulo(self):
        try:
            archivo_biblia = f"Biblia_{self.app.idioma_actual.upper()}.txt"
            path_biblia_activa = os.path.join(DIR_DATA, archivo_biblia)
            if not os.path.exists(path_biblia_activa): return

            def normalizar(txt):
                return "".join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn').upper()

            cap_norm = str(self.app.capitulo_actual_lector)
            cap_siguiente = str(int(cap_norm) + 1) if cap_norm.isdigit() else "2"
            
            ETIQUETAS_CAP = {
                "es": ["CAPÍTULO", "CAPITULO", "SALMO", "SALMOS"],
                "en": ["CHAPTER", "PSALM", "PSALMS"],
                "fr": ["CHAPITRE", "PSAUME", "JEAN", "CHRONIQUES", "ROIS", "SAMUEL"],
                "it": ["CAPITOLO", "SALMO", "SALMI"],
                "por": ["CAPÍTULO", "CAPITULO", "SALMO", "LIVRO", "O LIVRO"]
            }
            tags = ETIQUETAS_CAP.get(self.app.idioma_actual, ETIQUETAS_CAP["es"])

            with open(path_biblia_activa, 'r', encoding='utf-8') as f:
                lineas_biblia = f.readlines()

            capitulo_texto = []
            libro_norm = normalizar(self.app.libro_actual_lector)
            libro_raiz = libro_norm.replace("SAN ", "").replace("S. ", "").strip()
            dentro_del_libro = False

            for i, linea in enumerate(lineas_biblia):
                l_limp = linea.strip()
                if not l_limp: continue
                l_norm = normalizar(l_limp)

                if not dentro_del_libro:
                    if len(l_limp) < 30 and (libro_norm in l_norm or libro_raiz in l_norm):
                        dentro_del_libro = True
                    continue

                if dentro_del_libro:
                    if re.search(rf"\b{cap_norm}[:\.]1\b", l_norm) or any(l_norm == f"{normalizar(t)} {cap_norm}" for t in tags) or f"CAPITOLO {cap_norm}" in l_norm or f"CHAPTER {cap_norm}" in l_norm:
                        for j in range(i, len(lineas_biblia)):
                            lj_limp = lineas_biblia[j].strip()
                            if not lj_limp: continue
                            lj_norm = normalizar(lj_limp)
                            es_siguiente = re.search(rf"\b{cap_siguiente}[:\.]1\b", lj_norm) or any(lj_norm == f"{normalizar(t)} {cap_siguiente}" for t in tags) or f"CAPITOLO {cap_siguiente}" in lj_norm or f"CHAPTER {cap_siguiente}" in lj_norm
                            if es_siguiente and j > i: break
                            capitulo_texto.append(lj_limp)
                        break

            if capitulo_texto:
                texto_unificado = " ".join(capitulo_texto)
                texto_unificado = re.sub(r'(\d+:\d+|\b\d+\b)\s+', r'\n\1 ', texto_unificado)
                lineas_desglosadas = [l.strip() for l in texto_unificado.split('\n') if l.strip()]

                bloques_procesados = []
                for bloque in lineas_desglosadas:
                    bloque_norm = normalizar(bloque)
                    if bloque_norm in ["CAPITULO", "CAPÍTULO", "CHAPTER", "CHAPITRE", "CAPITOLO"] or re.match(r"^(CAPITULO|CAPÍTULO|CHAPTER|CHAPITRE|CAPITOLO|LIBRO|BOOK|LIVRO|LIVRE)\s+(I|II|III|IV|V|\d+)$", bloque_norm):
                        continue

                    match_prefijo = re.search(r"^(\d+[:\.]\d+|\d+)\s*(.*)$", bloque)
                    if match_prefijo:
                        val_izq = match_prefijo.group(1)
                        cuerpo = match_prefijo.group(2).strip()
                        
                        if ":" in val_izq: num_ver_real = val_izq.split(":")[1]
                        elif "." in val_izq: num_ver_real = val_izq.split(".")[1]
                        else: num_ver_real = val_izq
                        
                        if (num_ver_real == cap_norm or num_ver_real == "1") and len(cuerpo) < 60 and not cuerpo.lower().startswith("en el principio") and not cuerpo.lower().startswith("así dice"):
                            bloques_procesados.append(("titulo", cuerpo))
                        else:
                            prefijo = f"{cap_norm}:{num_ver_real} "
                            bloques_procesados.append(("versiculo", prefijo, cuerpo))
                    else:
                        bloques_procesados.append(("titulo", bloque))

                self.construir_o_actualizar_ventana_lectura(bloques_procesados)
        except:
            pass

    def construir_o_actualizar_ventana_lectura(self, bloques_procesados):
        ui_strings = DICCIONARIO_UI.get(self.app.idioma_actual, DICCIONARIO_UI["es"])
        LIMITE_CARACTERES = 80

        def renderizar_texto_en_area(area_txt):
            area_txt.config(state="normal")
            area_txt.delete("1.0", tk.END)
            area_txt.tag_configure("centrado", justify="center", foreground="#00ffcc", font=("Ubuntu", self.app.tamano_fuente_lector - 1, "bold"))
            area_txt.tag_configure("normal_ver", justify="left")
            
            if self.app.modo_cebra:
                area_txt.tag_configure("cebra_0", background="#141923")
                area_txt.tag_configure("cebra_1", background="#1c2333")

            versiculo_idx = 0
            for item in bloques_procesados:
                tipo = item[0]
                if tipo == "titulo":
                    area_txt.insert(tk.END, f"\n{item[1]}\n\n", "centrado")
                elif tipo == "versiculo":
                    prefijo = item[1]
                    cuerpo = item[2]
                    ancho_sangria = len(prefijo)
                    espacios_sangria = " " * (ancho_sangria + 4)
                    lineas_envueltas = textwrap.wrap(cuerpo, width=LIMITE_CARACTERES - (ancho_sangria + 4))
                    tag_cebra = f"cebra_{versiculo_idx % 2}" if self.app.modo_cebra else "normal_ver"
                    
                    if lineas_envueltas:
                        area_txt.insert(tk.END, f"{prefijo}{lineas_envueltas[0]}\n", tag_cebra)
                        for sub_linea in lineas_envueltas[1:]:
                            area_txt.insert(tk.END, f"{espacios_sangria}{sub_linea}\n", tag_cebra)
                    area_txt.insert(tk.END, "\n", "normal_ver")
                    versiculo_idx += 1

            area_txt.config(state="disabled")

        if hasattr(self.app, 'ventana_lectura') and self.app.ventana_lectura and self.app.ventana_lectura.winfo_exists():
            renderizar_texto_en_area(self.txt_area_lector)
            self.btn_libro.config(text=self.app.libro_actual_lector)
            self.btn_cap.config(text=self.app.capitulo_actual_lector)
            self.mostrar_vista_texto()
            return

        self.app.root.withdraw()
        self.app.ventana_lectura = tk.Toplevel()
        self.app.ventana_lectura.title("Lector")
        
        color_fondo_externo = "#0b0d10"      
        color_lienzo_texto = "#141923"      
        color_celeste_pastel = "#90dbf4"    
        color_crema_pergamino = "#f6f1e5"   
        color_borde_celestial = "#3a506b"   
        
        self.app.ventana_lectura.attributes("-fullscreen", True)
        self.app.ventana_lectura.configure(bg=color_fondo_externo)
        self.app.ventana_lectura.focus_set()

        self.app.ventana_lectura.bind("<Left>", lambda e: self.cambiar_capitulo_lector(-1))
        self.app.ventana_lectura.bind("<Right>", lambda e: self.cambiar_capitulo_lector(1))
        
        marco_interno = tk.Frame(self.app.ventana_lectura, bg=color_fondo_externo)
        marco_interno.pack(fill="both", expand=True)

        # 1. BARRA INFERIOR (Reservada primero para que el texto NUNCA la empuje fuera de pantalla)
        texto_boton = ui_strings.get("volver", "Volver (Esc)")
        btn_volver = tk.Button(marco_interno, text=texto_boton.upper(), bg="#1b202e", fg="#2196F3", font=("Ubuntu", 11, "bold"), activebackground="#252c3e", activeforeground="white", bd=1, relief="solid", padx=45, pady=8, cursor="hand2", command=self.cerrar_lectura)
        btn_volver.pack(side="bottom", pady=(10, 20))
        
        # 2. BARRA SUPERIOR
        marco_nav_sup = tk.Frame(marco_interno, bg=color_fondo_externo)
        marco_nav_sup.pack(side="top", fill="x", pady=(15, 10), padx=120)

        btn_cap_ant = tk.Button(marco_nav_sup, text=ui_strings["nav_cap_ant"], bg="#1b202e", fg=color_celeste_pastel, font=("Ubuntu", 11, "bold"), bd=1, relief="solid", padx=15, pady=4, cursor="hand2", command=lambda: self.cambiar_capitulo_lector(-1))
        btn_cap_ant.pack(side="left")

        marco_zoom = tk.Frame(marco_nav_sup, bg=color_fondo_externo)
        marco_zoom.pack(side="left", padx=(15, 0))

        btn_zoom_min = tk.Button(marco_zoom, text="A-", bg="#1b202e", fg="#90dbf4", font=("Ubuntu", 8, "bold"), bd=1, relief="solid", padx=6, pady=2, cursor="hand2", command=lambda: self.cambiar_tamano_fuente(-2))
        btn_zoom_min.pack(side="left", padx=2)

        btn_zoom_may = tk.Button(marco_zoom, text="A+", bg="#1b202e", fg="#90dbf4", font=("Ubuntu", 12, "bold"), bd=1, relief="solid", padx=6, pady=2, cursor="hand2", command=lambda: self.cambiar_tamano_fuente(2))
        btn_zoom_may.pack(side="left", padx=2)
        
        texto_btn_renglones = ui_strings.get("btn_renglones_si" if self.app.modo_cebra else "btn_renglones_no", "Renglones: ☑ Sí" if self.app.modo_cebra else "Renglones: ☐ No")
        self.btn_cebra_toggle = tk.Button(marco_zoom, text=texto_btn_renglones, bg="#1b202e", fg="#EAD2AC", font=("Ubuntu", 10, "bold"), bd=1, relief="solid", padx=8, pady=2, cursor="hand2", command=self.alternar_modo_lectura)
        self.btn_cebra_toggle.pack(side="left", padx=(10, 2))

        marco_buscador = tk.Frame(marco_nav_sup, bg=color_fondo_externo)
        marco_buscador.pack(side="left", expand=True)

        marco_botones_btn = tk.Frame(marco_buscador, bg=color_fondo_externo)
        marco_botones_btn.pack()

        self.btn_libro = tk.Button(marco_botones_btn, text=self.app.libro_actual_lector, bg="#1b202e", fg="#f6f1e5", font=("Ubuntu", 12, "bold"), width=16, bd=1, relief="solid", cursor="hand2", command=self.mostrar_vista_libros)
        self.btn_libro.pack(side="left", padx=5, ipady=3)

        self.btn_cap = tk.Button(marco_botones_btn, text=self.app.capitulo_actual_lector, bg="#1b202e", fg="#f6f1e5", font=("Ubuntu", 12, "bold"), width=4, bd=1, relief="solid", cursor="hand2", command=self.mostrar_vista_capitulos)
        self.btn_cap.pack(side="left", padx=5, ipady=3)

        lbl_pista = tk.Label(marco_buscador, text=ui_strings.get("pista_clic", "(Haz clic para cambiar)"), bg=color_fondo_externo, fg="#7a8b9e", font=("Ubuntu", 9, "italic"))
        lbl_pista.pack(pady=(2, 0))

        # Botón de cierre rápido superior a la derecha
        btn_cerrar_top = tk.Button(marco_nav_sup, text="✕", bg="#da3633", fg="white", font=("Ubuntu", 10, "bold"), bd=0, padx=8, pady=2, cursor="hand2", command=self.cerrar_lectura)
        btn_cerrar_top.pack(side="right", padx=(10, 0))

        btn_cap_sig = tk.Button(marco_nav_sup, text=ui_strings["nav_cap_sig"], bg="#1b202e", fg=color_celeste_pastel, font=("Ubuntu", 11, "bold"), bd=1, relief="solid", padx=15, pady=4, cursor="hand2", command=lambda: self.cambiar_capitulo_lector(1))
        btn_cap_sig.pack(side="right")

        nombre_version = NOMBRES_BIBLIAS.get(self.app.idioma_actual, "Biblia")
        lbl_biblia_version = tk.Label(marco_nav_sup, text=nombre_version.upper(), bg=color_fondo_externo, fg="#FFD700", font=("Ubuntu", 11, "bold"))
        lbl_biblia_version.pack(side="right", padx=(0, 15))

        # 3. CONTENIDO PRINCIPAL (Ocupa el espacio que queda libre entre la barra superior e inferior)
        self.marco_contenido = tk.Frame(marco_interno, bg=color_fondo_externo)
        self.marco_contenido.pack(side="top", fill="both", expand=True)

        self.marco_texto = tk.Frame(self.marco_contenido, bg=color_fondo_externo)
        self.txt_area_lector = scrolledtext.ScrolledText(self.marco_texto, wrap=tk.NONE, bg=color_lienzo_texto, fg=color_crema_pergamino, font=("Ubuntu", self.app.tamano_fuente_lector), highlightbackground=color_borde_celestial, highlightthickness=1, bd=0, width=70)
        self.txt_area_lector.pack(fill="both", expand=True)
        
        renderizar_texto_en_area(self.txt_area_lector)
        self.txt_area_lector.bind("<Key>", lambda e: "break")

        self.marco_libros = tk.Frame(self.marco_contenido, bg=color_fondo_externo)
        lista_nombres = LIBROS_BIBLIA.get(self.app.idioma_actual, LIBROS_BIBLIA["es"])
        
        lbl_at = tk.Label(self.marco_libros, text=ui_strings.get("at", "ANTIGUO TESTAMENTO"), bg=color_fondo_externo, fg="#00D4FF", font=("Ubuntu", 12, "bold"))
        lbl_at.grid(row=0, column=0, columnspan=6, pady=(0, 5))

        for i in range(39):
            nombre_lib = lista_nombres[i]
            btn = tk.Button(self.marco_libros, text=nombre_lib, bg="#141923", fg="#00ffcc", font=("Ubuntu", 10, "bold"), bd=1, relief="solid", activebackground="#3a506b", activeforeground="white", cursor="hand2", command=lambda l=nombre_lib: self.ejecutar_seleccion_libro(l))
            btn.grid(row=1 + (i//6), column=i%6, sticky="nsew", padx=2, pady=2)

        lbl_nt = tk.Label(self.marco_libros, text=ui_strings.get("nt", "NUEVO TESTAMENTO"), bg=color_fondo_externo, fg="#00D4FF", font=("Ubuntu", 12, "bold"))
        lbl_nt.grid(row=8, column=0, columnspan=6, pady=(15, 5))

        for i in range(39, 66):
            nombre_lib = lista_nombres[i]
            idx_nt = i - 39
            btn = tk.Button(self.marco_libros, text=nombre_lib, bg="#141923", fg="#00ffcc", font=("Ubuntu", 10, "bold"), bd=1, relief="solid", activebackground="#3a506b", activeforeground="white", cursor="hand2", command=lambda l=nombre_lib: self.ejecutar_seleccion_libro(l))
            btn.grid(row=9 + (idx_nt//6), column=idx_nt%6, sticky="nsew", padx=2, pady=2)

        for col in range(6):
            self.marco_libros.grid_columnconfigure(col, weight=1)

        self.marco_capitulos = tk.Frame(self.marco_contenido, bg=color_fondo_externo)
        self.mostrar_vista_texto()
        
        self.app.ventana_lectura.bind("<Escape>", lambda e: self.cerrar_lectura())

    def cerrar_lectura(self):
        if hasattr(self.app, 'ventana_lectura') and self.app.ventana_lectura:
            self.app.ventana_lectura.destroy()
            self.app.ventana_lectura = None
        self.app.root.deiconify()
        self.app.actualizar_interfaz()
