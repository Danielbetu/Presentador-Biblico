#!/bin/bash

# Este script se usa para ejecutar el programa Python de forma segura.

# Navega al directorio del script (importante dentro de un Flatpak).
cd "$(dirname "$0")"

# Ejecuta el script de Python
/usr/bin/python3 Mostrar_versiculo.py
