import os
import json
import time
import shutil
import urllib.parse
import re

from Constant import exp

import urllib.request
from getpass import getuser
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
import aspose.words as aw

import os
import time
import platform
import subprocess
# from pyngrok import ngrok
from pyngrok import ngrok, conf
from dotenv import load_dotenv

# from multiprocessing.pool import ThreadPool

# import aspose.imaging as imaging

request_logs = []
DD = 'tmp'

def cache(suministro):
    path = f'/home/{getuser()}/Documents/test/py/pdf'
    os.makedirs(path, exist_ok=True)
    
    pdf_filename = f"{suministro}.pdf"
    if pdf_filename in os.listdir(path):
        return os.path.join(path, pdf_filename)
    else:
        return None

def SearchFileWeb(suministro):
    global wait
    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 60)
    driver.get('https://hasbercourier.easyenvios.com/')

    sandbox = wait.until(EC.presence_of_element_located((By.ID, exp.box)))
    sandbox.send_keys(suministro)

    sendContent = wait.until(EC.presence_of_all_elements_located((By.XPATH, exp.btn)))
    sendContent[0].click()

    time.sleep(2)

    table_send = wait.until(EC.presence_of_all_elements_located((By.XPATH, exp.table)))
    for n_ in range(len(table_send)):
        table_tr = wait.until(EC.presence_of_element_located((By.XPATH,exp.tr.replace('@',f'{n_+1}')))).click()
        info = wait.until(EC.presence_of_element_located((By.ID,'sp_cargo_documento'))).text
        if 'CARTAS / REEMPLAZO DE MEDIDOR EMPRESAS' == info:
            time.sleep(2)
            Framesubdoc = wait.until(EC.presence_of_element_located((By.ID, exp.subdoc))).get_attribute('src')
            driver.quit()
            print(Framesubdoc)
            return Framesubdoc, suministro
        else:
            pass

def UrlSubdoc(Framesubdoc):
    ParsedUrl = urlparse(Framesubdoc)
    QueryParams = parse_qs(ParsedUrl.query)
    Url = QueryParams.get('url', [None])[0]
    return Url

def FileWebDownloads(url, suministro):
    try:
        if url != 'http://www.easyenvios.com/escan1/006/003/3/00000001/01/00300000001000001.TIF':
            filename = suministro + '.tif'
            with urllib.request.urlopen(urllib.request.Request(url)) as response, open(filename, "wb") as out_file:
                data = response.read()
                out_file.write(data)
            return filename
        else:
            return None
    except Exception as e:
        print(f"Error al descargar el archivo: {e}")
        return None

def ConvertPdf(filename):
    if filename:
        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        builder.insert_image(filename)
        pdf_filename = filename.replace('.tif', '.pdf')
        doc.save(pdf_filename)
        return pdf_filename
    else:
        return None

def Templades(pdf_filename):
    if pdf_filename:
        path = f'/home/{getuser()}/Documents/test/py/pdf'
        os.makedirs(path, exist_ok=True)

        shutil.move(pdf_filename, os.path.join(path, pdf_filename))
        os.remove(pdf_filename.replace('.pdf', '.tif'))
    else:
        print("No se encontró el archivo PDF para aplicar la plantilla.")

def ConsultApi(ip, port, endpoint, key_data, suministro):
    
    # Si no se encuentra en la caché, procede con la solicitud
    url = f"http://{ip}:{port}/{endpoint}"

    data = {
        "suministro": suministro
    }

    data_bytes = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'}, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            data_r = result.get(key_data)
            # Registrar la solicitud y la respuesta
            # log_request(suministro,data_r,filename='request_logs.json')
            if data_r is None:
                return 
            return data_r
        
    except urllib.error.HTTPError as e:
        print(f'Error HTTP: {e.code} - {e.reason}')
    except urllib.error.URLError as e:
        print(f'Error URL: {e.reason}')
    
    return None

def Directorios(directorio):
    def Servidor(func):
        def python(*args,**kwargs):
            if directorio:
                target_dir = os.path.join(os.getcwd(),directorio)  # Subdirectorio

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            os.chdir(target_dir)
            return func(*args, **kwargs)  # Ejecutar la función original
        return python
    return Servidor


from multiprocessing.pool import ThreadPool
import threading

urlTunnel = None
lock = threading.Lock()  # Crear un lock para asegurar el acceso a urlTunnel
servicios_iniciados = False

# -------- importaciones necesarias sino causa errores al momento de combinarlo con flask cuando se llama a Servicios
from multiprocessing.synchronize import Lock
from multiprocessing.queues import SimpleQueue
from multiprocessing.dummy import Process

@Directorios(DD)
def ServicioPython():
    so = platform.system() 
    python = 'python3' if so == 'Linux' else 'python'
    subprocess.Popen([f"{python}", "-m", "http.server", "5090"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('[+] Corriendo Servidor Python')

def ServicioNgrok():
    # Cargar el archivo .env
    load_dotenv(dotenv_path='/home/kimshizi/Documents/test/py/token.env')
    # Obtener el token de acceso desde el archivo .env
    token_ngrok = os.getenv('access')
    ngrok.set_auth_token(token_ngrok)  # Asegúrate de establecer el token antes de conectar
    tunnel = ngrok.connect(5090, "http",subdomain="osise")
    print('[+] Corriendo Tunnel ngrok')

def Servicios():
    global urlTunnel, servicios_iniciados
    
    with lock:  # Proteger acceso a la bandera servicios_iniciados
        if servicios_iniciados:
            print("\n[!] Los servicios ya están en ejecución, no se reiniciarán\n")
            return  # No ejecutar los servicios si ya están corriendo
        servicios_iniciados = True  # Marcar los servicios como iniciados

    pool = ThreadPool(2)

    # Ejecutar funciones asíncronas sin los paréntesis
    pool.apply_async(ServicioPython)
    pool.apply_async(ServicioNgrok)

    time.sleep(2)  # Dar tiempo para que ngrok inicie

    # Obtener túneles de Ngrok
    tunnels = ngrok.get_tunnels()

    with lock:  # Bloquear antes de modificar urlTunnel
        urlTunnel = str(tunnels[0].public_url) if tunnels else None

    print("[+] Iniciando Los servicios")
    with lock:
        print("[+] Tunnel:", urlTunnel)

def obtener_url_tunnel():
    """Devuelve el valor actual de urlTunnel de forma segura."""
    with lock:
        return urlTunnel

def GoogleLents(driver,wait,tunnel,filename):
    # with open("/home/kimshizi/Documents/test/py/tmp/tunnel.json", "r") as archivo:
    #     rs = json.load(archivo)
    #     tunnel = rs.get('tunnel')

    # options = Options()
    # driver = webdriver.Firefox(options=options)
    # wait = WebDriverWait(driver, 10)
    # driver.get('https://www.google.com/?olud')

    list_information = []

    driver.execute_script("window.open('https://www.google.com/?olud', '');")
    driver.switch_to.window(driver.window_handles[-1])

    sandbox = wait.until(EC.presence_of_element_located((By.XPATH, exp.lents)))
    sandbox.send_keys(tunnel+'/'+filename)

    search = wait.until(EC.element_to_be_clickable((By.XPATH,exp.search))).click()
    translate = wait.until(EC.element_to_be_clickable((By.ID, 'ucj-3'))).click()

    # Localizar el contenedor principal
    container = wait.until(EC.presence_of_element_located((By.CLASS_NAME,exp.contenedor)))

    # Localizar todos los 'div' hijos dentro del contenedor
    child_divs = container.find_elements(By.XPATH,exp.elementos)

    # Obtener el texto de cada uno de los elementos
    for div in child_divs:
        result = re.sub(r'\D', '', div.text)
        if result:
            list_information.append(result)
            
    driver.close()
    driver.switch_to.window(driver.window_handles[0])    
    
    return list_information[0]


# Servicios()