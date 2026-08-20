import os
import re
import unicodedata
import tkinter as tk
from modulos.constantes import DIR_DATA, DICCIONARIO_UI


class BuscadorInteligente:
    def __init__(self, app):
        self.app = app
        self.app.destruir_menu_flotante()

        ui_strings = DICCIONARIO_UI.get(self.app.idioma_actual, DICCIONARIO_UI["es"])
        self.app.root.withdraw()
        
        self.win_busca = tk.Toplevel()
        self.win_busca.title(ui_strings["busc_titulo"])
        self.win_busca.attributes("-fullscreen", True)
        self.win_busca.configure(bg="#0b0d10")
        self.win_busca.focus_set()

        marco_interno = tk.Frame(self.win_busca, bg="#0b0d10")
        marco_interno.pack(fill="both", expand=True, padx=80, pady=40)

        lbl_tit = tk.Label(marco_interno, text=ui_strings["busc_titulo"], bg="#0b0d10", fg="#90dbf4", font=("Ubuntu", 16, "bold"))
        lbl_tit.pack(pady=(0, 15))

        marco_sup = tk.Frame(marco_interno, bg="#0b0d10")
        marco_sup.pack(fill="x", pady=5)

        tk.Label(marco_sup, text=ui_strings["busc_frase"], bg="#0b0d10", fg="#00ffcc", font=("Ubuntu", 12, "bold")).pack(side="left", padx=(0, 10))

        self.entry_busca = tk.Entry(marco_sup, bg="#141923", fg="#f6f1e5", font=("Ubuntu", 13), insertbackground="white", bd=1, relief="solid")
        self.entry_busca.pack(side="left", fill="x", expand=True, padx=10, ipady=4)
        self.entry_busca.focus()

        btn_ejecutar = tk.Button(marco_sup, text=ui_strings["busc_btn_buscar"], bg="#1b202e", fg="#90dbf4", font=("Ubuntu", 11, "bold"), bd=1, relief="solid", padx=20, pady=4, cursor="hand2", command=self.ejecutar_busqueda)
        btn_ejecutar.pack(side="right")
        self.win_busca.bind('<Return>', lambda e: self.ejecutar_busqueda())

        marco_opciones = tk.Frame(marco_interno, bg="#0b0d10")
        marco_opciones.pack(fill="x", pady=(5, 5))

        self.var_palabra_exacta = tk.BooleanVar(value=True)
        chk_exacta = tk.Checkbutton(marco_opciones, text=ui_strings["busc_exacta"], variable=self.var_palabra_exacta, bg="#0b0d10", fg="#90dbf4", selectcolor="#141923", activebackground="#0b0d10", activeforeground="#90dbf4", font=("Ubuntu", 10))
        chk_exacta.pack(side="left")

        self.lbl_contador = tk.Label(marco_opciones, text="", bg="#0b0d10", fg="#00ffcc", font=("Ubuntu", 10, "bold"))
        self.lbl_contador.pack(side="right")

        tk.Label(marco_interno, text=ui_strings["busc_pauta"], bg="#0b0d10", fg="#EAD2AC", font=("Ubuntu", 11, "italic")).pack(pady=(5, 10))

        self.resultados_list = tk.Listbox(marco_interno, bg="#141923", fg="#f6f1e5", font=("Ubuntu", 12), selectbackground="#3a506b", selectforeground="white", bd=1, relief="solid", highlightthickness=0)
        self.resultados_list.pack(fill="both", expand=True, pady=10)
        self.resultados_list.bind("<Double-Button-1>", self.seleccionar_resultado)

        texto_boton = ui_strings.get("volver", "Volver (Esc)")

        btn_volver = tk.Button(marco_interno, text=texto_boton.upper(), bg="#1b202e", fg="#2196F3", font=("Ubuntu", 11, "bold"), activebackground="#252c3e", activeforeground="white", bd=1, relief="solid", padx=45, pady=10, cursor="hand2", command=self.cerrar_buscador)
        btn_volver.pack(side="bottom", pady=(15, 0))

        self.win_busca.bind("<Escape>", lambda e: self.cerrar_buscador())

    def cerrar_buscador(self):
        if self.win_busca:
            self.win_busca.destroy()
            self.win_busca = None
        self.app.root.deiconify()
        self.app.actualizar_interfaz()

    def ejecutar_busqueda(self):
        frase = self.entry_busca.get().strip()
        if not frase: return

        ui_strings = DICCIONARIO_UI.get(self.app.idioma_actual, DICCIONARIO_UI["es"])

        self.resultados_list.delete(0, tk.END)
        self.lbl_contador.config(text="")
        self.resultados_list.insert(tk.END, ui_strings["busc_buscando"])
        self.win_busca.update()

        archivo_biblia = f"Biblia_{self.app.idioma_actual.upper()}.txt"
        path_biblia = os.path.join(DIR_DATA, archivo_biblia)

        if not os.path.exists(path_biblia):
            self.resultados_list.delete(0, tk.END)
            self.resultados_list.insert(tk.END, ui_strings["busc_error_archivo"].format(archivo_biblia))
            return

        def normalizar(txt):
            nfkd = unicodedata.normalize('NFD', txt)
            return "".join(c for c in nfkd if unicodedata.category(c) != 'Mn').upper()

        frase_norm = normalizar(frase)
        es_exacta = self.var_palabra_exacta.get()
        
        if es_exacta:
            patron = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(frase_norm)}(?![A-Za-z0-9_])", re.UNICODE)
        
        resultados = []

        with open(path_biblia, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

        libro_actual, capitulo_actual, versiculo_actual = "LIBRO", "1", "1"
        ultimo_versiculo_fr = ""
        SUBTITULOS_IGNORAR = [
            "CAPITOLO", "LA CONSOLAZIONE", "TAU", "ALEPH", "BETH", "GIMEL", "DALETH", 
            "HE", "VAU", "ZAIN", "CHETH", "TETH", "JOD", "CAPH", "LAMED", "MEM", 
            "NUN", "SAMECH", "AIN", "PE", "TSADDI", "KOPH", "RESH", "SCHIN",
            "LIBRO I", "LIBRO II", "LIBRO III", "LIBRO IV", "LIBRO V",
            "BOOK I", "BOOK II", "BOOK III", "BOOK IV", "BOOK V",
            "LIVRO I", "LIVRO II", "LIVRO III", "LIVRO IV", "LIVRO V",
            "LIVRE I", "LIVRE II", "LIVRE III", "LIVRE IV", "LIVRE V"
        ]
        for linea in lineas:
            linea_limpia = linea.strip()
            if not linea_limpia: continue
            linea_norm = normalizar(linea_limpia)

            if self.app.idioma_actual == "fr" and re.match(r"^\d+\.\d+$", linea_limpia):
                ultimo_versiculo_fr = linea_limpia
                continue
            
            match_ver_memoria = re.match(r"^(\d+)\b", re.sub(r"^\d{4,}\s+", "", linea_limpia))
            if match_ver_memoria and len(match_ver_memoria.group(1)) <= 3:
                versiculo_actual = match_ver_memoria.group(1)

            if len(linea_limpia) < 30 and linea_limpia.isupper() and not re.search(r"\d+[:\.]\d+", linea_limpia):
                es_subtitulo = any(sub in linea_norm for sub in SUBTITULOS_IGNORAR)
                if not es_subtitulo and "CHAPTER" not in linea_norm and "CAPITOLO" not in linea_norm:
                    libro_limpio = re.sub(r"^\d+\s+", "", linea_limpia).strip()
                    if libro_limpio:
                        libro_actual, capitulo_actual, versiculo_actual = libro_limpio, "1", "1"

            match_cap = re.search(r"(?:CHAPTER|CAPITULO|CAPÍTULO|CAPITOLO|GENESE)\s+(\d+)", linea_norm)
            if match_cap:
                capitulo_actual, versiculo_actual = match_cap.group(1), "1"

            coincide = patron.search(linea_norm) if es_exacta else (frase_norm in linea_norm)

            if coincide:
                linea_proc = re.sub(r"^\d{4,}\s+", "", linea_limpia)
                match_cita_estandar = re.search(r"^(?:(\d*\s*[A-Za-z\s]+?)\s+)?(\d+[:\.]\d+)\s*[-–—]?\s*(.*)", linea_proc)
                match_ver_inicial = re.match(r"^(\d+)\b", linea_proc)
                
                if match_cita_estandar:
                    libro_linea = match_cita_estandar.group(1)
                    num_cita = match_cita_estandar.group(2)
                    if libro_linea and len(libro_linea.strip()) > 1 and not any(sub in normalizar(libro_linea) for sub in SUBTITULOS_IGNORAR):
                        cita = f"{libro_linea.strip().upper()} {num_cita}"
                    else:
                        cita = f"{libro_actual} {num_cita}"
                    cuerpo_texto = match_cita_estandar.group(3).strip()
                elif match_ver_inicial and len(match_ver_inicial.group(1)) <= 3:
                    num_ver = match_ver_inicial.group(1)
                    cita = f"{libro_actual} {capitulo_actual}:{num_ver}"
                    cuerpo_texto = linea_proc
                elif self.app.idioma_actual == "fr" and ultimo_versiculo_fr:
                    num_ver_fr = ultimo_versiculo_fr.split('.')[-1] if '.' in ultimo_versiculo_fr else ultimo_versiculo_fr
                    cita = f"{libro_actual} {capitulo_actual}:{num_ver_fr}"
                    cuerpo_texto = linea_proc
                else:
                    cita = f"{libro_actual} {capitulo_actual}:{versiculo_actual}"
                    cuerpo_texto = linea_proc

                texto_recortado = cuerpo_texto[:180] + "..." if len(cuerpo_texto) > 180 else cuerpo_texto
                resultados.append(f"{cita} - {texto_recortado}")

        self.resultados_list.delete(0, tk.END)
        if resultados:
            self.lbl_contador.config(text=ui_strings["busc_coincidencias"].format(len(resultados)))
            for r in resultados:
                self.resultados_list.insert(tk.END, r)
        else:
            self.lbl_contador.config(text=ui_strings["busc_cero_coincidencias"])
            self.resultados_list.insert(tk.END, ui_strings["busc_no_encontrado"])

    def seleccionar_resultado(self, event):
        if not self.resultados_list.curselection(): return
        seleccion = self.resultados_list.get(self.resultados_list.curselection())
        if " - " in seleccion:
            cita = seleccion.split(" - ")[0]
            try:
                partes = cita.rsplit(' ', 1)
                self.app.libro_actual_lector = partes[0].strip().upper()
                numeros = partes[1].strip()
                if ":" in numeros: self.app.capitulo_actual_lector = numeros.split(':')[0]
                elif "." in numeros: self.app.capitulo_actual_lector = numeros.split('.')[0]
                else: self.app.capitulo_actual_lector = numeros

                if self.win_busca:
                    self.win_busca.destroy()
                    self.win_busca = None

                self.app.guardar_configuracion()
                self.app.abrir_capitulo_completo()
            except:
                pass
