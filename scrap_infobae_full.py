# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 19:29:54 2024

@author: Diego
"""


from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import unicodedata
from scrap_utilities import requests_retry_session
from selenium.webdriver import Chrome


def scrap_infobae():
    # dirección de la homepage del medio
    diario_str = "https://www.infobae.com/"
    
    # ruta a tu WebDriver
    driver = Chrome('\chromedriver')
    # entrar al sitio
    driver.get(diario_str)
    # busca elementos con enlaces
    elements = driver.find_elements_by_xpath("//a[@href]")
    links1 = [l.get_attribute('href') for l in elements]
    # cierro el WebDriver
    driver.close()
    
    # filtra enlaces cortos como -https://www.infobae.com/economia/-
    links11 = [lnk for lnk in links1 if len(lnk)>60]
    # finalmente, enlaces únicos
    links = list(set(links11))    

    # formato en que se encuentra la fecha para luego parsear con datetime.datetime.strptime(string, format)
    format = "%d %b, %Y %I:%M %p"

    # diccionario de base para el DataFrame
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}

    # intenta iterar sobre cada enlace
    for link in links:
        try:
            # request sobre el enlace para obtener su html y luego parsearlo con BeautifulSoup
            response_p = requests_retry_session().get(link, 
                                                      verify = False, 
                                                      timeout=30, 
                                                      headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            # puede ser con html5lib, html.parser
            parser = BeautifulSoup(html_p, 'html5lib')

            # string de la fecha a partir del tag span con clase 'sharebar-article-date', luego se reemplaza '.' por ''
            fecha_str = parser.find('span',{'class':'sharebar-article-date'}).text.replace('.', '')
            # objeto datetime de la fecha
            fecha = datetime.strptime(fecha_str[:-4], format)

            # todos los tags correspondiente a párrafos en el html
            nota_tags = parser.findAll('p', {'class':'paragraph'})
            # se arma la string a partir del texto de cada tag y luego se la normaliza
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)    
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')

            # a cada clave del diccionario se le agrega el elemento correspondiente
            pakete_dict['fecha'].append(fecha)
            pakete_dict['link'].append(link)
            pakete_dict['texto'].append(nota)
            # si no existe un código alfanumérico dentro del link para identificar a la noticia, se utiliza el mismo enlace
            pakete_dict['idnota'].append(link)
    
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
    path = 'infobae_{}.csv'.format(datehour).replace(' ', '_').replace(':', '')
    # se guarda el .csv
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_infobae()
