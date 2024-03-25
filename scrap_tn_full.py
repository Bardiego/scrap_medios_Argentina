# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 15:56:47 2020

@author: Diego
"""


from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import unicodedata
from scrap_utilities import try_itr1
from scrap_utilities import requests_retry_session

def scrap_tn():
    diario_str = 'https://tn.com.ar'

    response = requests_retry_session().get(diario_str, 
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0'})
    html = response.text
    soup = BeautifulSoup(html, 'html5lib')
    
    articulos = soup.findAll('article')
    links = list(try_itr1(articulos, diario_str, AttributeError))
    
    format = "%d de %B %Y, %H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[], 'idnota':[]}
    
    
    
    for link in links:
        try:
            
            response_p = requests_retry_session().get(link, timeout=30, verify = False, headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html5lib') 
            fecha_hora = parser.find('span', {'class':'time__value'}).text[:-2]
            fecha_hora_publicacion = datetime.strptime(fecha_hora, format)
            nota_tags = parser.findAll('p')
            nota = str()
            nota = nota.join(tag.text for tag in nota_tags)  
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            pakete_dict['fecha-hora'].append(fecha_hora_publicacion)
            pakete_dict['link'].append(link)
            pakete_dict['idnota'].append(link)
            pakete_dict['noticia'].append(nota)
        except:
            pass
        
    for nota in pakete_dict['noticia']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
    
    df = pd.DataFrame.from_dict(data = pakete_dict)
    df = df.drop_duplicates(subset='idnota')
    
    datehour = datetime.today().strftime('%Y-%m-%d %H:%M')
    path = 'tn_{}.csv'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_tn()
    