# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 14:20:58 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import unicodedata
from scrap_utilities import requests_retry_session
from scrap_utilities import try_itr1
import locale



def scrap_cronica():    
    diario_str = 'https://www.cronica.com.ar'
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')

    ## Acá cambie el fake user
    response = requests_retry_session().get(diario_str, 
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})
    html = response.text
    soup = BeautifulSoup(html, 'html5lib')
    mylinks = soup.findAll('article')
    mylinks = list(try_itr1(mylinks, diario_str, AttributeError, TypeError))
    links = list(set(mylinks))
    
    format = "%d de %B %Y %H:%M"
    
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}
    
    for link in links:
        try:
            response_p = requests_retry_session().get(link, timeout=30, verify = False, 
                                                      headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_str = parser.find('time', {'class':'nota-fecha'}).text +' '+ parser.find('time', {'class':'nota-hora'}).text[:-3]
            fecha= datetime.strptime(fecha_str, format)

            cuerpo_nota =  parser.find('div', {'class':'notabody'})
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')

            idnota = link
            
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
    path = 'cronica_{}'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_cronica()
    
    
    