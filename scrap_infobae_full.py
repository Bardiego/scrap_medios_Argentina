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
    
    # 
    driver = Chrome('\chromedriver')
    driver.get(diario_str)
    elements = driver.find_elements_by_xpath("//a[@href]")
    links1 = [l.get_attribute('href') for l in elements]
    driver.close()

    links11 = [lnk for lnk in links1 if len(lnk)>60]
    links = list(set(links11))    
    
    format = "%d %b, %Y %I:%M %p"
    
    pakete_dict = {'fecha':[], 'link':[], 'texto':[], 'citas':[], 'idnota':[]}
    
    for link in links:
        try:
            response_p = requests_retry_session().get(link, 
                                                      verify = False, 
                                                      timeout=30, 
                                                      headers = {"User-Agent":'Mozilla/5.0'})
            html_p = response_p.text
            parser = BeautifulSoup(html_p, 'html5lib')
            
            fecha_str = parser.find('span',{'class':'sharebar-article-date'}).text.replace('.', '')
            fecha = datetime.strptime(fecha_str[:-4], format)
            
            nota_tags = parser.findAll('p', {'class':'paragraph'})
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
    path = 'infobae_{}.csv'.format(datehour).replace(' ', '_').replace(':', '')
    df.to_csv(path)
    
    

if __name__ == '__main__' :
    scrap_infobae()
