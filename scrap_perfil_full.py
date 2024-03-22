# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 23:32:09 2019

@author: Diego
"""


from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import locale
import re
import unicodedata
from scrap_utilities import try_itr1
from scrap_utilities import new_itr
from scrap_utilities import requests_retry_session
import pytz

def scrap_perfil():
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    diario_str = "https://www.perfil.com"      

    response = requests_retry_session().get(diario_str, 
                                            verify = False, 
                                            headers = {"User-Agent":'Mozilla/5.0'})
    html = response.text
    soup = BeautifulSoup(html, 'html5lib')
    myarticles = soup.findAll('article', {'class':'news'})       
    mylinks = list(try_itr1(myarticles, '', AttributeError))        
    sstr = diario_str+"/noticias/"
    links = list(new_itr(mylinks, sstr, '', len(sstr)))
        
    format = "%Y-%m-%dT%H:%M:%S.%fZ"
    
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}
    
    for link in links:
        try:
            response_p = requests_retry_session().get(link, timeout=30, verify = False, headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html5lib')

            fecha_str = parser.find('time').get('datetime')
            fecha = datetime.strptime(fecha_str, format)
            fecha = pytz.utc.localize(fecha).astimezone(pytz.timezone('America/Argentina/Buenos_Aires'))
            fecha = datetime.strptime(str(fecha)[:-6], "%Y-%m-%d %H:%M:%S")
            
            nota_tags = parser.find('div', {'id':'article-content'}).findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags) 
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            
            pakete_dict['fecha'].append(fecha)
            pakete_dict['link'].append(link)
            pakete_dict['texto'].append(nota)
            pakete_dict['idnota'].append(link)
        except:
            pass
        
    for nota in pakete_dict['texto']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
        
    df = pd.DataFrame.from_dict(data = pakete_dict)
    df = df.drop_duplicates(subset='idnota')
    
    datehour = datetime.today().strftime('%Y-%m-%d %H:%M')
    
    path = 'perfil_{}'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_perfil()

  