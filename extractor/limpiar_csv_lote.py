import pandas as pd
import glob
import os
import sys
import codecs

# Configura la salida estándar para que acepte caracteres UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), "replace")

# 📂 Definir la carpeta base con una ruta ABSOLUTA (en Desktop)
carpeta_base = r"C:\Users\Usuario\Desktop\CSVExtractorProyect\inputs"

# 📂 Carpeta de salida donde se guardan los archivos limpios
carpeta_salida = r"C:\Users\Usuario\Desktop\CSVExtractorProyect\clean_inputs"
os.makedirs(carpeta_salida, exist_ok=True)

# 📌 Columnas a eliminar
columnas_a_eliminar = [
    "is_spending_on_ads",
    "can_claim",
    "owner_name",
    "owner_profile_link",
    "is_temporarily_closed",
    "query"
]

# 🔍 Buscar todos los archivos .csv en la carpeta inputs
archivos_encontrados = glob.glob(os.path.join(carpeta_base, "*.csv"))

# Verificar si hay archivos en la carpeta
if not archivos_encontrados:
    print(f"❌ No se encontraron archivos CSV en la carpeta: {carpeta_base}")
else:
    for archivo in archivos_encontrados:
        try:
            df = pd.read_csv(archivo, encoding="utf-8", sep=",")

            print(f"Columnas en {os.path.basename(archivo)}: {df.columns.tolist()}")
            columnas_encontradas = [col for col in columnas_a_eliminar if col in df.columns]
            print(f"Columnas a eliminar: {columnas_encontradas}")

            if columnas_encontradas:
                df.drop(columns=columnas_encontradas, inplace=True)

            archivo_salida = os.path.join(carpeta_salida, os.path.basename(archivo))
            df.to_csv(archivo_salida, index=False, encoding="utf-8")

            print(f"✅ Archivo limpio guardado: {archivo_salida}")

        except Exception as e:
            print(f"❌ Error al procesar {os.path.basename(archivo)}: {e}")
