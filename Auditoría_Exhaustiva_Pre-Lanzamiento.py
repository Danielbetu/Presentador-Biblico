import os, json, re

dir_data = os.path.expanduser("~/Presentador_Biblico/data")
json_path = os.path.join(dir_data, "versiculos_favoritos_multilenguaje.json")

idiomas = {
    "ES": "Versiculos_biblicos_favoritos_ES.txt",
    "EN": "Versiculos_biblicos_favoritos_EN.txt",
    "FR": "Versiculos_biblicos_favoritos_FR.txt",
    "IT": "Versiculos_biblicos_favoritos_IT.txt",
    "POR": "Versiculos_biblicos_favoritos_POR.txt"
}

print("==================================================")
print("🔍 INICIANDO AUDITORÍA EXHAUSTIVA PRE-LANZAMIENTO")
print("==================================================\n")

# 1. Auditoría de los archivos .TXT
datos_idiomas = {}
errores_totales = 0

for lang, filename in idiomas.items():
    path = os.path.join(dir_data, filename)
    if not os.path.exists(path):
        print(f"❌ ARCHIVO NO ENCONTRADO: {filename}")
        errores_totales += 1
        continue

    with open(path, "r", encoding="utf-8") as f:
        contenido = f.read().strip()

    bloques = [b.strip() for b in contenido.split("\n\n") if b.strip()]
    entradas = []
    
    print(f"📄 Analizando {filename} ({len(bloques)} bloques encontrados)...")

    for idx, b in enumerate(bloques):
        lineas = [l.strip() for l in b.split("\n") if l.strip()]
        
        # Estructura básica de 2 líneas
        if len(lineas) != 2:
            print(f"  ⚠️ [Línea bloque #{idx+1}] Estructura irregular ({len(lineas)} líneas en lugar de 2):")
            print(f"     -> {lineas[0][:60]}...")
            errores_totales += 1
            continue

        texto, cita_raw = lineas[0], lineas[1]

        # Chequeo de cita pegada o texto desbordado
        if len(cita_raw) > 70:
            print(f"  ⚠️ [Bloque #{idx+1}] Cita sospechosamente larga (posible texto pegado): {cita_raw[:50]}...")
            errores_totales += 1

        # Chequeo de texto muy corto
        if len(texto) < 10:
            print(f"  ⚠️ [Bloque #{idx+1}] Texto sospechosamente corto: {texto}")
            errores_totales += 1

        cita_limpia = re.sub(r"\s+(RVR1960|KJV|LSG|RIV|ARC|NVI|DHH)$", "", cita_raw, flags=re.IGNORECASE).strip()
        entradas.append((cita_limpia, texto))

    datos_idiomas[lang] = entradas
    print(f"  ✅ {lang}: {len(entradas)} versículos validados correctamente.\n")

# 2. Control de alineación entre idiomas
print("🌐 Verificando paridad entre los 5 idiomas...")
cantidades = {lang: len(entradas) for lang, entradas in datos_idiomas.items()}

if len(set(cantidades.values())) != 1:
    print(f"❌ DESALINEACIÓN DE CANTIDADES EN ARCHIVOS TXT: {cantidades}")
    errores_totales += 1
else:
    print(f"  ✅ Paridad exacta: Todos los archivos TXT tienen {list(cantidades.values())[0]} citas.\n")

# 3. Auditoría del JSON multilenguaje
print("📦 Verificando versiculos_favoritos_multilenguaje.json...")
if not os.path.exists(json_path):
    print("❌ ARCHIVO JSON NO ENCONTRADO.")
    errores_totales += 1
else:
    with open(json_path, "r", encoding="utf-8") as f:
        data_json = json.load(f)

    keys_es = [c[0] for c in datos_idiomas.get("ES", [])]
    json_keys = list(data_json.keys())

    if len(json_keys) != len(keys_es):
        print(f"⚠️ Cantidad de citas en JSON ({len(json_keys)}) difiere del TXT de Español ({len(keys_es)}).")
        errores_totales += 1

    # Revisión clave por clave en las 5 lenguas
    for cita, idiomas_dict in data_json.items():
        for l_code in ["es", "en", "fr", "it", "por"]:
            if l_code not in idiomas_dict or not idiomas_dict[l_code].strip():
                print(f"  ❌ Falta traducción de [{l_code}] en la cita: {cita}")
                errores_totales += 1

print("\n==================================================")
if errores_totales == 0:
    print("🎉 ¡AUDITORÍA COMPLETA SIN ERRORES! EL PROYECTO ESTÁ 100% LIMPIO.")
else:
    print(f"⚠️ SE ENCONTRARON {errores_totales} OBSERVACIONES PARA CORREGIR.")
print("==================================================")

