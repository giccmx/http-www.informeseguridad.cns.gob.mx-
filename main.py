import os
import io
import time
import shutil
import logging
import requests
import warnings
import traceback
import pdfplumber
import pandas as pd
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

def get_url_cns(url,type_query):
  
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

        return str(url+'/'+href_a), texto_p
    
    else:
        return filas
    
  except Exception as e:
      
      traceback.print_exc()
      logging.error(str(e))

def table_extractor(pdf_url):
  
  try:
    
    response = requests.get(pdf_url)
    response.raise_for_status()
    pdf_file = io.BytesIO(response.content)

    with pdfplumber.open(pdf_file) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables({
            'vertical_strategy':'text',
            'horizontal_strategy':'text',
            'intersection_tolerance':5,
            })
    
    tables = tables[-1:]

    for i, table in enumerate(tables):
        
        table = [[v for v in sub if v] for sub in table if any(v for v in sub if v)]
        df = pd.DataFrame(table)

    df1 = df.iloc[:, [0, 1]][:-1].rename(columns={0: 'Entidades', 1:'recuento'})
    df2 = df.iloc[:, [-2, -1]][:-1].rename(columns={2: 'Entidades', 3:'recuento'})

    infseg = pd.concat([df1,df2], ignore_index=True).dropna()

    infseg = infseg.sort_values(by=infseg.columns[-1], ascending=False)
    infseg['recuento'] = infseg['recuento'].astype(int)
    infseg = infseg[infseg['recuento']!=0].reset_index(drop=True)
    total_dia = int(infseg['recuento'].sum())
    recuento_entidades = int(infseg['Entidades'].count())

    logging.info(f'Total de homicidios del día: {str(total_dia)}')
    logging.info(f'Total de Entidades que reportaron homicidio: {str(recuento_entidades)}')
    logging.info('Fuente: '+pdf_url)
    logging.info(infseg)

    logging.info('*'*100)

    return infseg, total_dia, recuento_entidades

  except Exception as e:
    
    traceback.print_exc()
    logging.error(str(e))

def clean_log():

    nombre_archivo = 'informeseguridadcnsgobmx.log'

    string_a_eliminar = 'WARNING - CropBox missing from /Page, defaulting to MediaBox'

    nombre_temp_archivo =  nombre_archivo + ".temp"

    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo_original, \
                open(nombre_temp_archivo, 'w', encoding='utf-8') as archivo_temporal:
            
            for linea in archivo_original:
                
                if string_a_eliminar not in linea:
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

        rows = get_url_cns(url,'weekend')

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

            table_extractor(url+'/'+href_a)
        
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

    logging.getLogger("pdfminer").setLevel(logging.WARNING)
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
                
                url, fecha = get_url_cns(fuente,'dayli')
                table_extractor(url)
                last_date(date_convert(fecha))

        except Exception as e:

            traceback.print_exc()
            logging.error('Ocurrió un error :'+str(e))

        finally:

            logging.info(str(format_time_exec(inicio)))
            clean_log()
    
    else:
        
        logging.info('Día inhabil')  
