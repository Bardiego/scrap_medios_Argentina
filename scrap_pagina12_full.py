# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 13:02:27 2019

@author: Diego
"""

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import locale
import re
import unicodedata
from scrap_utilities import try_itr1
from scrap_utilities import requests_retry_session


def scrap_pagina12():
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    diario_str = "https://www.pagina12.com.ar/"
    
    response = requests_retry_session().get(diario_str,
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0'})
    html = response.text
    soup = BeautifulSoup(html, 'html5lib')
    articulos = soup.findAll('article')
    links_ = list(try_itr1(articulos, ''))
    links_ = [link for link in links_ if re.search(r'/(\d+)-', link) != None]
    links = list(set(links_))
    
    format = "%d de %B de %Y - %H:%M"
    
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}
    
    for link in links:
        try:        
            response_p = requests_retry_session().get(link, 
                                                      timeout=30, 
                                                      verify = False, 
                                                      headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html5lib')
            
            fecha_str = parser.find('time').text
            fecha = datetime.strptime(fecha_str, format)
            
            cuerpo_nota = parser.find('div', {'class':'article-text'})
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            
            idnota = re.search(r'/(\d+)-', link).group(1)
            
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
    path = 'pagina12_{}'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_pagina12()
    
    
