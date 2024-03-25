# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 13:25:49 2019

@author: Diego
"""
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import locale
import re
import unicodedata
from scrap_utilities import requests_retry_session
from scrap_utilities import try_itr1

def scrap_lanacion():   
    # setear la condiguración regional en español (para las fechas por si acaso)
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    diario_str = 'https://www.lanacion.com.ar/'

    # requests_retry_session se utiliza por si hay que realizar una retry al sitio y setear algunos parámetros útiles
    response = requests_retry_session().get(diario_str, 
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0'})
    # html del sitio
    html = response.text
    # luego se parsea con BeautifulSoup, puede ser con html5lib, html.parser
    soup = BeautifulSoup(html, 'html5lib')
    # se buscan los tags con enlaces a noticias
    mydivs = soup.findAll('div', {'class':'grid-item'})
    # con la función try_itr1 se buscan los href de cada tag, evadiendo errores, y agregándole la string correspondiente al diario
    links = list(try_itr1(mydivs, diario_str, AttributeError))

    # formato en que se encuentra la fecha para luego parsear con datetime.datetime.strptime(string, format)
    format = "%d de %B de %Y %H:%M"

    # diccionario de base para el DataFrame
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}

    # intenta iterar sobre cada enlace
    for link in links:
        try:
            # requests_retry_session se utiliza en caso de necesitarse una retry al sitio y setear algunos parámetros útiles
            response_p = requests_retry_session().get(link, 
                                                      timeout=30, 
                                                      verify = False, 
                                                      headers = {"User-Agent":'Mozilla/5.0'})
            # html del sitio
            html_p = response_p.text
            # luego se parsea con BeautifulSoup, puede ser con html5lib, html.parser
            parser = BeautifulSoup(html_p, 'html5lib')   

            # string de la fecha a partir del tag time con clase 'com-date' y 'com-hour'
            fecha_str= parser.find('time', {'class':'com-date'}).text + ' ' + parser.find('time', {'class':'com-hour'}).text
            # objeto datetime de la fecha
            fecha = datetime.strptime(fecha_str, format)

            # todos los tags correspondiente a párrafos en el html
            nota_tags = parser.findAll('p', {'class':'com-paragraph --s'})
            # se arma la string a partir del texto de cada tag y luego se la normaliza
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')

            # a cada clave del diccionario se le agrega el elemento correspondiente
            pakete_dict['fecha'].append(fecha)
            pakete_dict['link'].append(link)
            # si no existe un código alfanumérico dentro del link para identificar a la noticia, se utiliza el mismo enlace
            pakete_dict['idnota'].append(link)
            pakete_dict['texto'].append(nota)
        except:
            pass
    
    # de cada texto se extraen los fragmentos entre comillas
    for nota in pakete_dict['texto']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        # se agrega una lista de citas al diccionario
        pakete_dict['citas'].append(citas1)

    # DataFrame a partir del diccionario
    df = pd.DataFrame.from_dict(data = pakete_dict)
    # se eliminan elementos duplicados a partir del identificador de la nota
    df = df.drop_duplicates(subset='idnota')

    # fecha y hora en que se termina de ejecutar el código
    datehour = datetime.today().strftime('%Y-%m-%d %H:%M')
    # la ruta contiene el nombre del medio junto con la fecha y hora de ejecución del código
    path = 'lanacion_{}.csv'.format(datehour).replace(' ', '_').replace(':', '')
    # finalmente se guarda el .csv
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_lanacion()
