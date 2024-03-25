# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:41:04 2024

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

def scrap_elcanciller():   
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    diario_str = 'https://elcanciller.com/'
    
    response = requests_retry_session().get(diario_str, 
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0'})
    html = response.text
    soup = BeautifulSoup(html, 'html5lib')
    
    frontpage = soup.find('div', {'is':'page-front'})
    divs_frontpage = frontpage.findAll('div')
    links = list(set(list(try_itr1(divs_frontpage, diario_str, AttributeError, TypeError))))
    
    format = "%A %d de %B de %Y %H:%M"
    
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}
    
    for link in links:
        try:
            response_p = requests_retry_session().get(link, 
                                                      timeout=30, 
                                                      verify = False, 
                                                      headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html5lib')   
            
            fecha_str= parser.find('time').text
            fecha = datetime.strptime(fecha_str, format)
            
            nota_tags = parser.findAll('div', {'class':'article-body-content'})
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            
            idnota = link[-25:]
            
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
    path = 'elcanciller_{}'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_elcanciller()
