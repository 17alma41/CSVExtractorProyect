import pandas as pd
import os

def modificar_columnas_csv(
    ruta_entrada: str,
    ruta_salida: str = None,
    nuevo_orden: list = None,
    renombrar_columnas: dict = None
):
    """
    Modifica el orden y/o nombres de las columnas en un CSV.

    :param ruta_entrada: Ruta del archivo CSV original.
    :param ruta_salida: Ruta donde se guardará el nuevo archivo (si no se especifica, sobrescribe el original).
    :param nuevo_orden: Lista con el nuevo orden de columnas.
    :param renombrar_columnas: Diccionario con columnas a renombrar.
    """
    try:
        df = pd.read_csv(ruta_entrada)

        if renombrar_columnas:
            df.rename(columns=renombrar_columnas, inplace=True)

        if nuevo_orden:
            # Validar que todas las columnas existan antes de reordenar
            if not set(nuevo_orden).issubset(df.columns):
                columnas_faltantes = set(nuevo_orden) - set(df.columns)
                raise ValueError(f"Las siguientes columnas no existen en el archivo: {columnas_faltantes}")
            df = df[nuevo_orden]

        if ruta_salida is None:
            ruta_salida = ruta_entrada

        df.to_csv(ruta_salida, index=False)
        print(f"✅ Archivo guardado en: {ruta_salida}")
    except Exception as e:
        print(f"❌ Error al modificar columnas: {e}")


def procesar_csvs_en_carpeta(
    carpeta_outputs: str = "outputs",
    nuevo_orden: list = None,
    renombrar_columnas: dict = None
):
    """
    Procesa todos los CSV en la carpeta:
    - Renombra y reordena columnas si todas existen.
    - NO crea columnas vacías.
    - NO elimina los originales.
    """
    for archivo in os.listdir(carpeta_outputs):
        if archivo.endswith(".csv") and not archivo.endswith("_mod.csv"):
            ruta_entrada = os.path.join(carpeta_outputs, archivo)
            nombre_base = archivo[:-4]
            ruta_salida = os.path.join(carpeta_outputs, f"{nombre_base}.csv")

            print(f"Modificando columnas de {archivo}...")

            modificar_columnas_csv(
                ruta_entrada=ruta_entrada,
                ruta_salida=ruta_salida,
                nuevo_orden=nuevo_orden,
                renombrar_columnas=renombrar_columnas
            )
