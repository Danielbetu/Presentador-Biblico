import os
import json
import tkinter as tk

def verificar_y_mostrar_bienvenida(app_instance):
    """
    Verifica en config.json si es el primer arranque de la app.
    Si lo es, programa la apertura del cartel de bienvenida en el idioma correspondiente.
    """
    # Buscamos la ruta de la carpeta data
    dir_base_app = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_data = os.path.join(dir_base_app, "data")
    config_path = os.path.join(dir_data, "config.json")
    
    es_primer_arranque = True

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                es_primer_arranque = data.get("primer_arranque", True)
        except Exception:
            pass

    if es_primer_arranque:
        # Programamos el cartel 3.2 segundos después del inicio (tras el splash screen)
        app_instance.root.after(3200, lambda: _mostrar_cartel(app_instance, config_path))

def _mostrar_cartel(app, config_path):
    """Dibuja la ventana flotante multilingüe de bienvenida."""
    win_welcome = tk.Toplevel(app.root)
    win_welcome.overrideredirect(True)
    
    ancho_w, alto_w = 540, 240
    x = app.root.winfo_x() + (app.ancho_pantalla // 2) - (ancho_w // 2)
    y = app.root.winfo_y() + (app.alto_pantalla // 2) - (alto_w // 2)
    win_welcome.geometry(f"{ancho_w}x{alto_w}+{x}+{y}")
    win_welcome.configure(bg="#1e1e1e", highlightbackground="#00ffcc", highlightthickness=1)
    
    # Obtenemos los textos traducidos
    from PresentadorBiblicoV2 import DICCIONARIO_UI
    ui_strings = DICCIONARIO_UI.get(app.idioma_actual, DICCIONARIO_UI["es"])
    
    tk.Label(
        win_welcome, 
        text=ui_strings.get("bienvenida_tit", "¡BIENVENIDO!"), 
        bg="#1e1e1e", fg="#00ffcc", font=("Ubuntu", 12, "bold")
    ).pack(pady=(20, 10))
    
    tk.Label(
        win_welcome, 
        text=ui_strings.get("bienvenida_body", ""), 
        bg="#1e1e1e", fg="white", font=("Ubuntu", 11), 
        justify="center", wraplength=500
    ).pack(pady=10)
    
    def guardar_y_cerrar():
        # Marcamos la variable en la instancia de la app
        app_instance.primer_arranque = False
        
        # Guardamos en config.json usando el método de la app
        if hasattr(app_instance, 'guardar_configuracion'):
            app_instance.guardar_configuracion()
        else:
            # Respaldo por si acaso
            config_data = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                except Exception:
                    pass
            config_data["primer_arranque"] = False
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=4)
            except Exception:
                pass
            
        win_welcome.destroy()

    tk.Button(
        win_welcome, 
        text=ui_strings.get("btn_aceptar", "Aceptar"), 
        bg="#333333", fg="white", font=("Ubuntu", 10, "bold"), 
        activebackground="#444", activeforeground="white", 
        bd=0, relief="flat", padx=25, pady=6, cursor="hand2", 
        command=guardar_y_cerrar
    ).pack(pady=(5, 10))
