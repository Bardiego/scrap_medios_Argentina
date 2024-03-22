# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 15:17:48 2019

@author: Diego
"""

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import locale
import unicodedata
from scrap_utilities import try_itr1
from scrap_utilities import requests_retry_session


def scrap_lacapitalrosario():
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    diario_str = 'https://www.lacapital.com.ar'
    
    response = requests_retry_session().get(diario_str, 
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0'})
    html = response.text
    soup = BeautifulSoup(html, 'html5lib')
    myarticles = soup.findAll('article')
    links = list(try_itr1(myarticles,  '', AttributeError, TypeError))

    format = "%d de %B %Y %H:%Mhs"
    
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}
    
    for link in links:
        try:
            response_p = requests_retry_session().get(link, 
                                                      timeout=30, 
                                                      verify = False, 
                                                      headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html5lib')

            fecha_str = parser.find('div', {'class':'fecha-container'}).find('span', {'class':'nota-fecha'}).text +' '+parser.find('div', {'class':'fecha-container'}).find('span', {'class':'nota-hora'}).text
            fecha = datetime.strptime(fecha_str, format)
            
            cuerpo_nota = parser.findAll('div', {'class':'article-body'})
            cuerpo_nota_ = [i.findAll('p') for i in cuerpo_nota]              
            nota_tags = [x for xs in cuerpo_nota_ for x in xs]
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)    
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            
            pakete_dict['fecha'].append(fecha)
            pakete_dict['link'].append(link)
            pakete_dict['idnota'].append(link)
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
    path = 'lacapitalrosario_{}'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_lacapitalrosario()
    
    
    
    