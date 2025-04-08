import pandas as pd


def generar_excel(df_resultado, nombre_archivo):
    excel_path = f"outputs/{nombre_archivo.replace('.csv', '')}.xlsx"
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # Hoja de datos
        df_resultado.to_excel(writer, sheet_name="datos", index=False)

        # Estadísticas
        estadisticas = {
            "Número de empresas": [len(df_resultado)],
            "Número de emails (válidos)": [df_resultado["email"].astype(bool).sum()],
            "Número de teléfonos": [df_resultado["phone"].astype(bool).sum()],
            "Teléfonos fijos": [df_resultado["phone"].str.extract(r'(\d+)')[0].dropna().apply(
                lambda x: str(x).startswith(("9", "8"))).sum()],
            "Teléfonos móviles": [df_resultado["phone"].str.extract(r'(\d+)')[0].dropna().apply(
                lambda x: str(x).startswith(("6", "7"))).sum()],
        }
        df_estadisticas = pd.DataFrame(estadisticas)
        df_estadisticas.to_excel(writer, sheet_name="estadísticas", index=False)

        # Sectores (main_category)
        if "main_category" in df_resultado.columns:
            df_sectores = df_resultado["main_category"].value_counts().reset_index()
            df_sectores.columns = ["Sector", "Número de empresas"]
            df_sectores.to_excel(writer, sheet_name="sectores", index=False)

        # Copyright
        copyright_text = """Aviso Legal
        © centraldecomunicacion.es. Todos los derechos reservados.
        Registrada ante la consejería de cultura y patrimonio histórico GR-00416-2020.
        https://www.centraldecomunicacion.es/

        Las fuentes de los datos son las páginas web oficiales de cada empresa.
        No manejamos datos personales, por lo que no aplican LOPD ni RGPD.

        La base de datos es intransferible y no replicable.
        Se prohíbe la copia, distribución o publicación total o parcial sin consentimiento expreso.
        Se tomarán medidas legales por infracciones de derechos de autor.

        Para más información, consulte nuestras preguntas frecuentes:
        https://www.centraldecomunicacion.es/preguntas-frecuentes-bases-de-datos/

        Queda prohibida la reproducción, distribución, comunicación pública y transformación, total o parcial,
        de los contenidos de esta base de datos, sin la autorización expresa de centraldecomunicacion.es.
        Los datos han sido recopilados de fuentes públicas y cumplen con la normativa vigente."""
        df_copyright = pd.DataFrame([line.split("\n") for line in copyright_text.split("\n")])
        df_copyright.to_excel(writer, sheet_name="copyright", index=False, header=False)

    print(f"📊 Excel generado con estadísticas y datos: {excel_path}")
