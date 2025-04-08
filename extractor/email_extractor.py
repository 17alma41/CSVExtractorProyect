import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        print(f"❌ Error inicializando ChromeDriver: {e}")
        return None


def extract_emails_from_url(url):
    driver = setup_driver()
    if not driver:
        return []

    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        time.sleep(2)  # dar tiempo a que cargue el contenido

        page_text = driver.page_source
        emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", page_text))
        return list(emails)

    except Exception as e:
        print(f"❌ Error en {url}: {e}")
        return []

    finally:
        driver.quit()
