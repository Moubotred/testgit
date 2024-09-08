import argparse
import ResourceHub as Rb  # Asumiendo que Rb es un módulo que has importado

ip = 'localhost'
port = '5000'
endpoint = 'procesar_imagen_suministro'
key_data = 'result'

def apiUrl(sum_value):
    """
    Consulta la API con un valor proporcionado y devuelve el resultado. 
    Si no existe un registro previo en el archivo JSON, realiza una solicitud a la API.

    Parameters:
    sum_value (str): El valor para realizar la consulta a la API.
    
    Returns:
    None: Imprime el resultado de la consulta.
    """
    rs = Rb.ConsultApi(ip, port, endpoint, key_data, sum_value)    
    print(rs)

def apiDoc(sum_value):
    """
    Consulta la API y procesa un documento si el resultado es un enlace a un archivo PDF o un enlace HTTPS.
    Si es un PDF, imprime la URL del documento.
    Si es un enlace HTTPS, descarga el archivo, lo convierte a PDF, y genera una plantilla de salida.

    Parameters:
    sum_value (str): El valor para realizar la consulta y procesamiento de documentos.
    
    Returns:
    None: Imprime la URL, o el archivo PDF procesado.
    """
    raw_url = Rb.ConsultApi(ip, port, endpoint, key_data, sum_value)    
    if raw_url.endswith('.pdf') or raw_url.startswith('https'):

        if raw_url.endswith('.pdf'):
            print(raw_url)

        elif raw_url.startswith('https'):
            url = Rb.UrlSubdoc(raw_url)
            filename = Rb.FileWebDownloads(url, sum_value)
            ff = Rb.ConvertPdf(filename)
            Rb.Templades(ff)
            print(ff)

    else:
        print(raw_url)

def apiImg(sum_value):
    """
    Función de reserva para procesar imágenes. Actualmente no implementada.

    Parameters:
    sum_value (str): El valor de entrada para procesar la imagen.
    
    Returns:
    None: Esta función aún no tiene implementación.
    """
    pass

def main():
    """
    Función principal que utiliza argparse para parsear los argumentos de la línea de comandos.
    Según el modo seleccionado ('apiUrl' o 'apiDoc'), llama a las funciones respectivas para consultar 
    la API o procesar documentos.

    Parameters:
    None: No toma parámetros directos, pero procesa los argumentos de la línea de comandos.
    
    Returns:
    None: Ejecuta la función correspondiente según el modo de operación.
    """
    parser = argparse.ArgumentParser(description="Herramienta de utilidad para procesar datos.")
    
    parser.add_argument('sum', type=str, help='Valor de suma o identificador.')
    parser.add_argument('--mode', type=str, choices=['apiUrl', 'apiDoc'], required=True,
                        help="Modo de operación: 'apiUrl' para consultar la API o verificar caché, 'apiDoc' para descargar y convertir.")

    args = parser.parse_args()

    if args.mode == 'apiUrl':
        apiUrl(args.sum)
    elif args.mode == 'apiDoc':
        apiDoc(args.sum)

if __name__ == '__main__':
    main()
