import random

import subprocess

import os

import time


# --- Configuración del Archivo (CORREGIDA) ---

# Esto busca el archivo .txt en la MISMA carpeta donde está este script .py

# No importa desde dónde se ejecute el programa, ahora siempre lo encontrará.

directorio_script = os.path.dirname(os.path.abspath(__file__))

NOMBRE_ARCHIVO = os.path.join(directorio_script, "Versiculos_biblicos_favoritos.txt")


def obtener_versiculos():

    versiculos = []

    bloque_actual = []

    

    try:

        with open(NOMBRE_ARCHIVO, 'r', encoding='utf-8') as f:

            for linea in f:

                linea = linea.strip()

                

                if linea:

                    bloque_actual.append(linea)

                elif bloque_actual:

                    cita = bloque_actual.pop()

                    cuerpo = '\n'.join(bloque_actual)

                    versiculo_completo = f"{cuerpo}\n\n— {cita}"

                    versiculos.append(versiculo_completo)

                    bloque_actual = []


            if bloque_actual:

                cita = bloque_actual.pop()

                cuerpo = '\n'.join(bloque_actual)

                versiculo_completo = f"{cuerpo}\n\n— {cita}"

                versiculos.append(versiculo_completo)


    except FileNotFoundError:

        return [f"Error: No encuentro el archivo en:\n{NOMBRE_ARCHIVO}"]

    except Exception as e:

        return [f"Error al leer el archivo: {e}"]


    return versiculos


def mostrar_versiculo_en_escritorio(versiculo):

    # Pausa para dar tiempo al escritorio a cargar

    time.sleep(10)

    

    versiculo_grande = f"<big><big><big><big>{versiculo}</big></big></big></big>"

    

    try:

        subprocess.run([

            'zenity', 

            '--info',

            '--title=🕊️ Versículo del Día', 

            '--text={}'.format(versiculo_grande),

            '--width=500'

        ], check=True)

    except Exception as e:

        # Si falla Zenity, intentamos imprimir en un log de error (opcional)

        print(f"Error visual: {e}")


# --- Ejecución Principal (CORREGIDA) ---

if __name__ == "__main__":

    lista_versiculos = obtener_versiculos()

    

    if lista_versiculos:

        # Elegimos uno al azar
        seleccionado = random.choice(lista_versiculos)
        mostrar_versiculo_en_escritorio(seleccionado)
