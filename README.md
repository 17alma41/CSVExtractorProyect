# 📬 Contacts Extractor

Este proyecto permite **extraer emails y redes sociales** desde sitios web listados en archivos `.csv`. Es ideal para obtener información de contacto de empresas de forma automática. 
Además de limpiar columnas del `.csv`.

---

## 🚀 Funcionalidades principales

- ✅ Extracción de **emails** desde el contenido de las webs usando Selenium.
- ✅ Extracción de **redes sociales esenciales**:
  - Facebook
  - Instagram
  - LinkedIn
  - Twitter/X
- ✅ Soporte para **múltiples archivos CSV** de entrada.
- ✅ Modo **demo** para pruebas rápidas.
- ✅ **Paralelización** con `ThreadPoolExecutor` para acelerar el scraping.
- ✅ Estructura modular lista para escalar y mantener.
- 🧹 Utilidad extra para **limpiar CSVs por lotes**.

---

## 🧱 Estructura del proyecto

```
CSVExtractorProyect/
├── main.py                        # Script principal
├── extractor/
│   ├── email_extractor.py        # Extracción de emails con Selenium
│   ├── social_extractor.py       # Extracción de redes sociales esenciales
│   ├── limpiar_csv_lote.py       # Limpieza masiva de CSVs
│   ├── utils.py                  # Funciones auxiliares
├── inputs/                       # Archivos CSV con webs a procesar
├── outputs/                      # ⚠️ Crear manualmente antes de ejecutar
├── requirements.txt              # Dependencias del proyecto
```

---

## ⚙️ Requisitos

1. **Python 3.8+**
2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Tener **Google Chrome instalado**.
4. Descargar el **ChromeDriver** que coincida con tu versión de Chrome:
   👉 [https://sites.google.com/chromium.org/driver/](https://sites.google.com/chromium.org/driver/)
5. Añadir `chromedriver.exe` al **PATH de Windows** o dejarlo en la raíz del proyecto.

---

## 🧪 Modo demo vs completo

Dentro de `main.py` puedes cambiar esta línea:

```python
DEMO_MODE = True
```

- `True` → toma 20 filas.
- `False` → procesa **todos los archivos CSV** completos.

---

## 🛠 Cómo usar

1. Coloca tus archivos `.csv` dentro de la carpeta `inputs/`.
   - El archivo debe tener una columna llamada `website`.

2. Crea la carpeta `outputs/` si no existe:
```bash
mkdir outputs
```

3. Ejecuta el script:

```bash
python main.py
```

4. Se generarán archivos en la carpeta `outputs/`, con nombre como:
```
emails_NombreDelArchivo.csv
```

---

## 📌 Ejemplo de columnas generadas

| website        | emails                 | facebook       | instagram     | linkedin      | twitter       |
|----------------|-------------------------|----------------|---------------|---------------|----------------|
| empresa.com    | contacto@empresa.com    | fb.com/empresa | insta.com/... | linkedin/...  | twitter.com/...|

---

## 📼 Tutorial en video

👉 [Ver ejemplo en YouTube](https://www.youtube.com/watch?v=jrNZQyhtBM0)

---

## 🧹 Limpieza por lotes

También puedes limpiar múltiples CSVs con el script:

```bash
python extractor/limpiar_csv_lote.py
```

Esto eliminará filas vacías o sin datos de interés.
Aunque no hace falta ejecutar este script porque ya lo realiza solo.
