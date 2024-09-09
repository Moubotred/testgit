import time
from queue import Queue
import Constant as C
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

import time
from flask import Flask, request, jsonify
import ResourceHub as Rb
import requests
import threading
from ResourceHub import Servicios
import Constant as C 

import json

app = Flask(__name__)

# Global variables for WebDriver and WebDriverWait
driver = None
wait = None

# decoraror para medir tiempo
def measure_time(func):
    """
    Decorador para medir el tiempo de ejecución de una función.
    
    Args:
        func: La función a decorar.
    
    Returns:
        wrapper: Función decorada que mide el tiempo de ejecución.
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            raise
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

# busca el frame que contiene la url
def shipping_charge(wait):
    """
    Determina el tipo de documento de carga basado en la información contenida
    en una tabla y devuelve la URL del frame del subdocumento asociado.

    Args:
        wait (WebDriverWait): Objeto de espera explícita para sincronizar
        el código con la carga de elementos en la página web.

    Returns:
        str: URL del frame del subdocumento si el documento es una carta 
        de reemplazo de medidor de empresas. Si el documento es un aviso 
        de corte, devuelve un mensaje específico. Si el documento es 
        postales, devuelve otro mensaje específico.

    Raises:
        No se especifican excepciones."""
    
    time.sleep(3)
    table_send = wait.until(EC.presence_of_all_elements_located((By.XPATH, C.exp.table)))
    for n_ in range(len(table_send)):
        table_tr = wait.until(EC.presence_of_element_located((By.XPATH,C.exp.tr.replace('@',f'{n_+1}')))).click()
        info = wait.until(EC.presence_of_element_located((By.ID,'sp_cargo_documento'))).text
        if 'CARTAS / REEMPLAZO DE MEDIDOR EMPRESAS' == info:
            wait.until(EC.presence_of_element_located((By.ID, C.exp.cargo))).click()
            Framesubdoc = wait.until(EC.presence_of_element_located((By.ID, C.exp.subdoc))).get_attribute('src')
            return Framesubdoc
        elif 'VOLANTES / AVISO DE CORTE' == info:
            return 'No METER CHANGE letter, only CUT NOTICE'
        elif 'RECIBO / POSTALES' == info:
            return 'No METER CHANGE letter, only POSTCARDS'

# carga el numero de suministro y lo envia    
@measure_time
def send_supply(wait, supply):
    """
    Interactúa con una página web para enviar un suministro y obtener un atributo del iframe.
    
    Args:
        wait: Objeto WebDriverWait para manejar las esperas explícitas.
        supply: El valor a enviar en el formulario.
    
    Returns:
        str: El valor del atributo 'src' del iframe.
    """
    try:
        time.sleep(2)
        sandbox = wait.until(EC.presence_of_element_located((By.ID, C.exp.box)))
        sandbox.send_keys(supply)

        sendContent = wait.until(EC.presence_of_all_elements_located((By.XPATH, C.exp.btn)))
        sendContent[0].click()

        rs = shipping_charge(wait)
        return rs

    except Exception as e:
        print(f"Error in send_supply: {e}")
        return None

# convierte documento a un pdf
@measure_time
def pdf_converter(response, supply):
    result = response.json()
    result_url = result.get('result')
    url_ = Rb.UrlSubdoc(result_url)
    filename = Rb.FileWebDownloads(url_, supply)
    ff = Rb.ConvertPdf(filename)
    Rb.Templades(ff)
    return ff

# maneja las peticiones en cola
def Supply_tail(driver, wait, supply):
    """
    Maneja la cola de suministros, abre nuevas pestañas, y llama a send_supply para un suministro.
    
    Args:
        driver: Instancia del WebDriver.
        wait: Objeto WebDriverWait para manejar las esperas explícitas.
        supply: Valor del suministro para procesar.
    
    Returns:
        str: Resultado del procesamiento del suministro.
    """
    queue = Queue()
    queue.put(supply)
    result = None

    while not queue.empty():
        element = queue.get()
        try:
            driver.execute_script("window.open('https://hasbercourier.easyenvios.com/', '');")
            driver.switch_to.window(driver.window_handles[-1])
            result = send_supply(wait, element)
        except Exception as e:
            print(f"Error processing element {element}: {e}")
            result = None
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    
    return result

# inicia el navegador
def init_browser():
    """
    Inicializa el WebDriver y abre la página principal al iniciar la aplicación.
    """
    global driver, wait
    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 60)
    try:
        driver.get('https://hasbercourier.easyenvios.com/')
        threading.Thread(target=Servicios, daemon=True).start()
    except Exception as e:
        print(f"Error opening main page: {e}")
        driver.quit()
        raise

# endpoint para obtener el frame y ver la url
@app.route('/process_supply', methods=['POST'])
def process_supply():
    """
    Endpoint para procesar un suministro.
    
    Expects:
        JSON body with a single suministro.
    
    Returns:
        JSON response with the result of processing the suministro.
    """
    data = request.json
    supply = data.get('suministro')
    
    if supply is None:
        return jsonify({"error": "You must provide a supply."}), 400
    try:
        result = Supply_tail(driver, wait, supply)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"result": result})

# endpoint para convertir el frame a un pdf
@app.route('/process_convert_pdf', methods=['POST'])
def process_convert_pdf():
    data = request.json
    supply = data.get('suministro')

    if supply is None:
        return jsonify({"error": "You must provide a supply."}), 400

    # # Call the endpoint that processes the supply and gets the PDF URL
    response = requests.post("http://localhost:5000/process_supply", json={"suministro": supply})
    if response.status_code != 200:
        return jsonify({"error": "Error processing the supply."}), response.status_code

    filename = pdf_converter(response, supply)
    
    return jsonify({"result": filename})

@app.route('/process_image_a_pdf', methods=['POST'])
def process_imagen_pdf():
    data = request.json
    supply = data.get('suministro')
    if supply is None:
        return jsonify({"error": "You must provide a supply."}), 400

    with open("/home/kimshizi/Documents/test/py/tmp/tunnel.json", "r") as archivo:
        rs = json.load(archivo)
        tunnel = rs.get('tunnel')
    
    suministro = Rb.GoogleLents(driver,wait,tunnel,supply)

    response = requests.post("http://localhost:5000/process_convert_pdf", json={"suministro": suministro})
    if response.status_code != 200:
        return jsonify({"error": "Error processing the supply."}), response.status_code

    result = response.json()
    result_name = result.get('result')

    return jsonify({"result":result_name})    

if __name__ == "__main__":
    init_browser()  # Initialize the browser when the application starts
    app.run(host='0.0.0.0', port=5000)