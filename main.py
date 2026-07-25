import os
import re
import fitz
import time
import shutil
import logging
import requests
import warnings
import traceback
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime

def format_time_exec(initial):
    try:
        fin = time.time()
        duracion = int(fin - initial)
        dias = duracion // 86400
        horas = (duracion % 86400) // 3600
        minutos = (duracion % 3600) // 60
        segundos = duracion % 60

        return f"Tiempo de ejecución: {dias:02d}:{horas:02d}:{minutos:02d}:{segundos:02d}"
    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))

def get_url_cns(url, type_query):
    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        filas = soup.find_all("tr")

        if type_query == 'dayli':
            ultima_fila = filas[1]
            p_tag = ultima_fila.find("p")
            a_tag = ultima_fila.find("a")

            texto_p = p_tag.get_text(strip=True) if p_tag else None
            href_a = a_tag.get("href") if a_tag else None

            logging.info(texto_p)

            return str(url + '/' + href_a), texto_p
        else:
            return filas
    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))

def table_extractor(pdf_url):
    """
    Descarga el PDF, extrae el texto de la primera página y genera el DataFrame
    limpio utilizando la lógica regex funcional.
    """
    try:
        # CORRECCIÓN: Usar pdf_url en lugar de url
        respuesta = requests.get(pdf_url)
        if respuesta.status_code != 200:
            raise Exception(f"Error al descargar el PDF: {respuesta.status_code}")

        archivo_pdf = BytesIO(respuesta.content)
        documento = fitz.open(stream=archivo_pdf, filetype="pdf")
        texto = documento[0].get_text()

        estados_validos = [
            'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche',
            'Chiapas', 'Chihuahua', 'Ciudad De México', 'Coahuila', 'Colima', 'Durango',
            'Estado De México', 'Guanajuato', 'Guerrero', 'Hidalgo', 'Jalisco', 'Michoacán',
            'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla', 'Querétaro', 'Quintana Roo',
            'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco', 'Tamaulipas', 'Tlaxcala',
            'Veracruz', 'Yucatán', 'Zacatecas'
        ]

        # Extraer usando regex
        patron = r'(\d{1,3})\s+([A-ZÁÉÍÓÚÑ\s]+)'
        coincidencias = re.findall(patron, texto)

        datos = [(estado.strip().title(), int(numero)) 
                 for numero, estado in coincidencias if "TOTAL" not in estado.upper()]

        # Crear y limpiar DataFrame
        df = pd.DataFrame(datos, columns=["Entidades", "Recuento"])
        df = df[df["Recuento"] > 0]
        df = df[df["Entidades"].isin(estados_validos)]
        
        # Ordenar de mayor a menor
        infseg = df.sort_values(by="Recuento", ascending=False).reset_index(drop=True)

        total_dia = int(infseg['Recuento'].sum())
        recuento_entidades = int(infseg['Entidades'].count())

        logging.info(f'Total de homicidios del día: {str(total_dia)}')
        logging.info(f'Total de Entidades que reportaron homicidio: {str(recuento_entidades)}')
        logging.info('Fuente: ' + pdf_url)
        logging.info("\n" + str(infseg))
        
        # Guardar en CSV usando el nombre del archivo PDF
        nombre_csv = pdf_url.split('/')[-1].replace('.pdf', '.csv')
        infseg.to_csv(nombre_csv, index=False)

        logging.info('*'*100)

        return infseg, total_dia, recuento_entidades

    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))
        return None, 0, 0

def clean_log():
    nombre_archivo = 'informeseguridadcnsgobmx.log'

    string_a_eliminar = [
        "WARNING - CropBox missing from /Page, defaulting to MediaBox", 
        "WARNING - Cannot set gray non-stroke color because /'P17' is an invalid float value",
        "WARNING - Cannot set gray non-stroke color because /'P31' is an invalid float value"
    ]

    nombre_temp_archivo = nombre_archivo + ".temp"

    try:
        for str_elim in string_a_eliminar:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo_original, \
                 open(nombre_temp_archivo, 'w', encoding='utf-8') as archivo_temporal:
                
                for linea in archivo_original:
                    if str_elim not in linea:
                        archivo_temporal.write(linea)
        
            shutil.move(nombre_temp_archivo, nombre_archivo)
            
    except FileNotFoundError:
        print(f"Error: El archivo '{nombre_archivo}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo: {e}")
        if os.path.exists(nombre_temp_archivo):
            os.remove(nombre_temp_archivo)

def get_nth_weekday(year, month, weekday, n):
    first_day = date(year, month, 1)
    days_to_add = (weekday - first_day.weekday() + 7) % 7
    first_weekday = first_day + timedelta(days=days_to_add)
    return first_weekday + timedelta(weeks=n - 1)

def holliday(fecha=None):
    if fecha is None:
        fecha = date.today()

    año = fecha.year

    dias_fijos = {
        (1, 1),
        (5, 1),
        (9, 16),
        (12, 25),
    }

    descanso_movil = {
        get_nth_weekday(año, 2, 0, 1),
        get_nth_weekday(año, 3, 0, 3),
        get_nth_weekday(año, 11, 0, 3),
    }

    dias_descanso = {date(año, mes, dia) for mes, dia in dias_fijos}
    dias_descanso.update(descanso_movil)

    return fecha in dias_descanso

def date_convert(date_str):
    try:
        meses = {
            "enero": "01",
            "febrero": "02",
            "marzo": "03",
            "abril": "04",
            "mayo": "05",
            "junio": "06",
            "julio": "07",
            "agosto": "08",
            "septiembre": "09",
            "octubre": "10",
            "noviembre": "11",
            "diciembre": "12"
        }
        
        try:
            for mes_es, mes_num in meses.items():
                if mes_es in date_str.lower():
                    partes = date_str.lower().replace(" de ", "-").split("-")
                    dia = partes[0]
                    mes = mes_num
                    anio = partes[2]
                    fecha_formateada = f"{dia}-{mes}-{anio}"
                    return datetime.strptime(fecha_formateada, '%d-%m-%Y').date()

            return None
        
        except Exception as e:
            traceback.print_exc()
            logging.error(str(e))

    except ValueError as e:
        print("Error al convertir la fecha:", e)
        return None

def last_date(fecha: datetime.date, ruta: str = "./last_date.txt"):
    try:
        with open(ruta, "w") as archivo:
            archivo.write(fecha.isoformat())
    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))

def get_data_weekend(url):
    try:
        update_final = None

        with open('./last_date.txt', "r") as archivo:
            fecha_str = archivo.read().strip()
            lastdate = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        rows = get_url_cns(url, 'weekend')

        for i, fila in enumerate(rows, start=0):
            p_tag = fila.find("p")
            a_tag = fila.find("a")

            if not p_tag or not a_tag:
                continue 

            texto_p = p_tag.get_text(strip=True)
            loop_date = date_convert(texto_p)

            if i == 1:
                update_final = loop_date

            logging.info(texto_p)
            href_a = a_tag.get("href")

            if loop_date == lastdate:
                break

            table_extractor(url + '/' + href_a)
        
        if update_final:
            last_date(update_final)

        return 'Done'

    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='informeseguridadcnsgobmx.log',
        filemode='w'
    )

    logging.getLogger("pdfplumber").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    warnings.filterwarnings("ignore")

    fuente = 'http://www.informeseguridad.cns.gob.mx'
          
    if holliday() == False:
        try:
            inicio = time.time()
            logging.info('*'*100)

            if datetime.today().strftime("%A") == 'Monday' or holliday(datetime.now().date() - timedelta(days=1)) == True:
                get_data_weekend(fuente)
            else:
                url, fecha = get_url_cns(fuente, 'dayli')
                table_extractor(url)
                
                fecha_convertida = date_convert(fecha)
                if fecha_convertida:
                    last_date(fecha_convertida)

        except Exception as e:
            traceback.print_exc()
            logging.error('Ocurrió un error :' + str(e))

        finally:
            logging.info(str(format_time_exec(inicio)))
            clean_log()
    else:
        logging.info('Día inhábil')