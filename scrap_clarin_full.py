# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 13:02:27 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import unicodedata
from scrap_utilities import try_itr1
from scrap_utilities import new_itr
from scrap_utilities import requests_retry_session
import locale

def scrap_clarin():
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
    diario_str = 'https://www.clarin.com'

    
    response = requests_retry_session().get(diario_str, 
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0'})
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    articulos = soup.findAll('article')
    links1 = list(try_itr1(articulos, '', AttributeError, TypeError))
    links = list(new_itr(links1, 'https://www.clarin.com' , '', len('https://www.clarin.com')))
    
    
    format = "%d/%m/%Y %H:%M"
    
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}

    for link in links:
        try:
            response_p = requests_retry_session().get(link, 
                                                      verify = False, 
                                                      timeout=30, 
                                                      headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html.parser')
            
            fecha_str = parser.find('span', {'class':'date'}).text
            fecha = datetime.strptime(fecha_str[:16], format)
            
            nota_tags = parser.find('div', {'class':'StoryTextContainer'})
            nota = str()
            nota = nota.join(tag.text for tag in nota_tags)  
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('\u200b', '').replace('\xa0', '').replace('\n', '')
            
            idnota = link[-15:-5]
            
            pakete_dict['fecha'].append(fecha)
            pakete_dict['link'].append(link)
            pakete_dict['idnota'].append(idnota)
            pakete_dict['texto'].append(nota)
        except:
            pass
    
    for nota in pakete_dict['texto']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
    
    df = pd.DataFrame.from_dict(data = pakete_dict)
    df = df.drop_duplicates(subset='idnota')
    
    datehour = datetime.today().strftime('%Y-%m-%d %H:%M')
    
    path = 'clarin_{}'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_clarin()
