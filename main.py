import os
import subprocess
import shutil
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url
from extractor.column_editor import procesar_csvs_en_carpeta
from extractor.generador_excel import  generar_excel

# 📂 Rutas de carpetas (IMPORTANTE: cambiar rutas)
EXTRACTOR_FOLDER = os.path.join(os.path.dirname(__file__), "extractor")
INPUT_FOLDER = os.path.join(os.path.dirname(__file__), "inputs")
CLEAN_INPUT_FOLDER = os.path.join(os.path.dirname(__file__), "clean_inputs")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "outputs")

# 🚀 Configuración
DEMO_MODE = True  # True para prueba, False para procesar
MAX_WORKERS = 5  # Ajusta según tu CPU/ChromeDriver
EMAIL_VERIFICATION_MODE = "avanzado"  # normal | avanzado | ultra-avanzado

# ⚙️ Configuración de columnas
NUEVO_ORDEN = ["name",
               "main_category",
               "categories",
               "reviews",
               "rating",
               "address",
               "website",
               "email",
               "phone",
               "facebook",
               "instagram",
               "linkedin",
               "x",
               "description",
               "competitors",
               "seo_keywords",
               "workday_timing",
               "closed_on",
               "featured_image",
               "google_link",
               "place_id"]

RENOMBRAR_COLUMNAS = {
    "review_keywords": "seo_keywords",
    "link": "google_link"
}


# Función para ejecutar la limpieza de los CSV
def ejecutar_script_limpieza():
    script_path = os.path.join(EXTRACTOR_FOLDER, "limpiar_csv_lote.py")

    if not os.path.exists(script_path):
        print(f"❌ No se encontró el script: {script_path}")
        exit(1)

    print(f"📂 Ejecutando limpieza con: {script_path}")
    python_exe = r"C:\\Users\\Usuario\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
    resultado = subprocess.run([python_exe, script_path], capture_output=True, text=True, encoding="utf-8")

    if resultado.returncode == 0:
        print("✅ Limpieza completada correctamente.")
    else:
        print(f"❌ Error en limpieza:\n{resultado.stderr}")


# Función para mover los archivos limpiados a la carpeta clean_inputs
def mover_archivo_limpio(nombre_archivo):
    archivo_origen = os.path.join(INPUT_FOLDER, nombre_archivo)
    archivo_destino = os.path.join(CLEAN_INPUT_FOLDER, nombre_archivo)

    if os.path.exists(archivo_origen):
        shutil.move(archivo_origen, archivo_destino)
        print(f"📂 Archivo movido a {CLEAN_INPUT_FOLDER}: {nombre_archivo}")
    else:
        print(f"❌ El archivo no se encuentra en {INPUT_FOLDER}: {nombre_archivo}")


# Función para procesar cada archivo limpio
def procesar_sitio(row):
    website = row["website"]
    print(f"🔍 Procesando {website}")
    emails = extract_emails_from_url(website, modo_verificacion=EMAIL_VERIFICATION_MODE)
    redes = extract_essential_social_links_from_url(website)

    return {
        **row,
        "email": ", ".join(emails),
        "facebook": ", ".join(redes.get("facebook", [])),
        "instagram": ", ".join(redes.get("instagram", [])),
        "linkedin": ", ".join(redes.get("linkedin", [])),
        "x": ", ".join(redes.get("x", []))
    }


# Función para procesar cada archivo CSV en clean_inputs
def procesar_archivo(nombre_archivo, demo_mode=False):
    path_entrada = os.path.join(CLEAN_INPUT_FOLDER, nombre_archivo)

    if os.path.getsize(path_entrada) == 0:
        print(f"❌ El archivo {nombre_archivo} está vacío.")
        return

    try:
        df = pd.read_csv(path_entrada)

        if "website" not in df.columns:
            print(f"❌ El archivo {nombre_archivo} no contiene columna 'website'")
            return

        if demo_mode:
            df = df.head(20)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            resultados = list(executor.map(procesar_sitio, [row for _, row in df.iterrows()]))

        df_resultado = pd.DataFrame(resultados)

        # Renombrar y reordenar columnas
        df_resultado.rename(columns=RENOMBRAR_COLUMNAS, inplace=True)
        df_resultado = df_resultado.reindex(columns=[col for col in NUEVO_ORDEN if col in df_resultado.columns])

        # Guardar CSV en la carpeta de salida
        output_path = os.path.join(OUTPUT_FOLDER, f"{nombre_archivo}")
        df_resultado.to_csv(output_path, index=False)
        print(f"✅ Datos guardados en {output_path}")

        # Generar Excel con múltiples hojas
        generar_excel(df_resultado, nombre_archivo)

    except pd.errors.EmptyDataError:
        print(f"❌ El archivo {nombre_archivo} está vacío o no tiene datos válidos.")
    except Exception as e:
        print(f"⚠️ Error al procesar {nombre_archivo}: {e}")


if __name__ == "__main__":
    # Paso 1: Limpieza de los archivos
    ejecutar_script_limpieza()

    if not os.path.exists(CLEAN_INPUT_FOLDER):
        print(f"❌ No se encontró la carpeta de entrada: {CLEAN_INPUT_FOLDER}")
        exit(1)

    # Paso 2: Mover los archivos limpiados a clean_inputs
    for archivo in os.listdir(INPUT_FOLDER):
        if archivo.endswith(".csv"):
            mover_archivo_limpio(archivo)

    # Paso 3: Procesar los archivos en clean_inputs
    for archivo in os.listdir(CLEAN_INPUT_FOLDER):
        if archivo.endswith(".csv"):
            procesar_archivo(archivo, demo_mode=DEMO_MODE)

    print("\n🔧 Reordenando y renombrando columnas de los archivos generados...")
    procesar_csvs_en_carpeta(
        carpeta_outputs=OUTPUT_FOLDER,
        nuevo_orden=NUEVO_ORDEN,
        renombrar_columnas=RENOMBRAR_COLUMNAS
    )
