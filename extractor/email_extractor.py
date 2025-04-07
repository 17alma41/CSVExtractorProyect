import pandas as pd
import dns.resolver
from tqdm import tqdm
import pyisemail
import os
from pathlib import Path
import smtplib

# Configuración de rutas (adaptar según necesidad)
CARPETA_BASE = Path("C:/Users/Usuario/PycharmProjects/CSVExtractorProyect")
CARPETA_INPUTS = CARPETA_BASE / "inputs"
CARPETA_OUTPUTS = CARPETA_BASE / "outputs"

# Asegurar que existen las carpetas
CARPETA_INPUTS.mkdir(parents=True, exist_ok=True)
CARPETA_OUTPUTS.mkdir(parents=True, exist_ok=True)


# Funciones de verificación
def verificar_formato_email(email):
    """Verifica que el formato del email sea correcto utilizando pyisemail."""
    return pyisemail.is_email(email, check_dns=False)


def verificar_dominio(email):
    """Verifica que el dominio del email tenga registros DNS válidos."""
    dominio = email.split('@')[-1]
    try:
        dns.resolver.resolve(dominio, 'A')
        return True
    except dns.exception.DNSException:
        return False


def verificar_MX(email):
    """Verifica que el dominio del email tenga registros MX válidos."""
    dominio = email.split('@')[-1]
    try:
        registros_mx = dns.resolver.resolve(dominio, 'MX')
        return len(registros_mx) > 0
    except dns.exception.DNSException:
        return False


def verificar_registros_SPF(dominio):
    """Verifica si el dominio tiene registros SPF válidos."""
    try:
        registros_spf = dns.resolver.resolve(dominio, 'TXT')
        for txt_record in registros_spf:
            if 'v=spf1' in str(txt_record).lower():
                return True
        return False
    except dns.exception.DNSException:
        return False


def verificar_registros_DMARC(dominio):
    """Verifica si el dominio tiene una política DMARC."""
    try:
        registros_dmarc = dns.resolver.resolve('_dmarc.' + dominio, 'TXT')
        for txt_record in registros_dmarc:
            if 'v=dmarc1' in str(txt_record).lower():
                return True
        return False
    except dns.exception.DNSException:
        return False


def verificar_registros_DKIM(dominio):
    """Verifica si el dominio tiene registros DKIM."""
    try:
        selectores = ['default', 'dkim', 'selector1', 'selector2', 'mail']
        for selector in selectores:
            registros_dkim = dns.resolver.resolve(f'{selector}._domainkey.{dominio}', 'TXT')
            for txt_record in registros_dkim:
                if 'v=dkim1' in str(txt_record).lower():
                    return True
        return False
    except dns.exception.DNSException:
        return False


def verificar_servidor_SMTP(email):
    """Verifica si el servidor SMTP del dominio está activo."""
    dominio = email.split('@')[-1]
    try:
        registros_mx = dns.resolver.resolve(dominio, 'MX')
        mx_record = str(min(registros_mx, key=lambda r: r.preference).exchange)
        server = smtplib.SMTP(timeout=5)
        server.connect(mx_record)
        server.quit()
        return True
    except Exception:
        return False


def verificar_disposable_email(email):
    """Verifica si el email es de un dominio desechable conocido."""
    disposable_domains = set(['mailinator.com', 'trashmail.com', 'tempmail.com', '10minutemail.com'])
    dominio = email.split('@')[-1]
    return dominio in disposable_domains


def verificar_existencia_email(email, modo='avanzado'):
    """Verifica la existencia del correo electrónico según el modo seleccionado."""
    resultados = {}
    if not verificar_formato_email(email):
        resultados['Formato'] = 'Formato inválido'
        return resultados
    else:
        resultados['Formato'] = 'Válido'

    if not verificar_dominio(email):
        resultados['Dominio'] = 'Dominio inválido'
        return resultados
    else:
        resultados['Dominio'] = 'Válido'

    if modo == 'normal':
        return resultados

    if not verificar_MX(email):
        resultados['MX'] = 'Sin registros MX'
        return resultados
    else:
        resultados['MX'] = 'Válido'

    if modo == 'avanzado':
        return resultados

    dominio = email.split('@')[-1]

    resultados['SPF'] = 'Válido' if verificar_registros_SPF(dominio) else 'Sin registros SPF'
    resultados['DMARC'] = 'Válido' if verificar_registros_DMARC(dominio) else 'Sin registros DMARC'
    resultados['DKIM'] = 'Válido' if verificar_registros_DKIM(dominio) else 'Sin registros DKIM'
    resultados['Dominio desechable'] = 'Sí' if verificar_disposable_email(email) else 'No'
    resultados['Servidor SMTP'] = 'Activo' if verificar_servidor_SMTP(email) else 'No responde'

    return resultados


def determinar_estado(resultados, modo):
    """Determina el estado final del email basado en los resultados de verificación."""
    if 'Formato' in resultados and resultados['Formato'] != 'Válido':
        return resultados['Formato']
    elif 'Dominio' in resultados and resultados['Dominio'] != 'Válido':
        return resultados['Dominio']
    elif modo == 'avanzado' and resultados.get('MX', '') != 'Válido':
        return resultados['MX']
    elif modo == 'ultra-avanzado':
        errores_ultra = [k for k, v in resultados.items() if v != 'Válido' and k not in ['Formato', 'Dominio']]
        if errores_ultra:
            return ', '.join([f"{k}: {v}" for k, v in resultados.items() if v != 'Válido'])
        else:
            return 'Válido'
    else:
        return 'Válido'


def listar_archivos_csv():
    """Lista todos los archivos CSV disponibles en la carpeta de inputs"""
    archivos = list(CARPETA_INPUTS.glob("*.csv"))
    if not archivos:
        print(f"No se encontraron archivos CSV en {CARPETA_INPUTS}")
        return None
    return archivos


def procesar_archivo_csv(archivo_csv, modo_verificacion='avanzado', columna_email='emails'):
    """Procesa el archivo CSV seleccionado"""
    try:
        df = pd.read_csv(archivo_csv)

        if columna_email not in df.columns:
            print(f"\n❌ Error: No se encontró la columna '{columna_email}' en el archivo.")
            print("Columnas disponibles:", list(df.columns))
            columna_email = input("Ingrese el nombre correcto de la columna con emails: ")
            if columna_email not in df.columns:
                raise ValueError("Columna de emails no encontrada")

        print(f"\nProcesando {len(df)} emails en modo '{modo_verificacion}'...")

        correos_validos = []
        for email in tqdm(df[columna_email], desc="Verificando emails"):
            if pd.isna(email):
                correos_validos.append('')  # Mantener los emails vacíos
                continue

            resultados = verificar_existencia_email(str(email).strip(), modo=modo_verificacion)
            estado = determinar_estado(resultados, modo=modo_verificacion)

            if estado == 'Válido':
                correos_validos.append(email)
            else:
                correos_validos.append('')  # Los inválidos se ponen vacíos

        # Reemplazar la columna 'emails' por los correos válidos
        df[columna_email] = correos_validos

        # Crear nombre de archivo de salida
        nombre_salida = f"{archivo_csv.stem}_verificado_{modo_verificacion}.csv"
        ruta_salida = CARPETA_OUTPUTS / nombre_salida

        df.to_csv(ruta_salida, index=False)
        print(f"\n✅ Resultados guardados en: {ruta_salida}")

        return df

    except Exception as e:
        print(f"\n❌ Error al procesar el archivo: {str(e)}")
        return None


def main():
    print("\n" + "=" * 50)
    print(" VERIFICADOR DE EMAILS DESDE ARCHIVO CSV ".center(50, '='))  # Encabezado del programa
    print("=" * 50)

    # Seleccionar archivo automáticamente
    archivo_csv = listar_archivos_csv()[0]  # Selecciona el primer archivo encontrado
    if not archivo_csv:
        return

    # Procesar archivo
    procesar_archivo_csv(archivo_csv, modo_verificacion='avanzado')


if __name__ == "__main__":
    main()
