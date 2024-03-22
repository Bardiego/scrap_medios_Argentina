# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 18:01:31 2020

@author: Diego
"""
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

## Función para realizar retries al consultar un sitio web, 
## Créditos https://gist.github.com/zduymz/1e8b0471e84b6244ed08d319179605e2
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

## Función para procesar los tags recibidos y obtener los enlaces a las noticias
def try_itr1(itr, diario_str, *exceptions):
    # itero sobre cada elemento
    for elem in itr:
        try:
            # intento obtener el enlace
            link = elem.find('a').get('href')
            # lo devuelvo con la cadena deseada
            yield diario_str+link
        except exceptions:
            pass

## Función para chequear si una dada cadena se encuentra en los enlaces
def new_itr(itr, string, diario_str, fin):
    # itero sobre cada elemento
    for elem in itr:
        # chequeo si la cadena que elijo esta en el enlace
        if string in elem[:fin]:
            yield(diario_str+elem)

# def buscar_citas(string):
#     citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', 
#                        string)
#     citas_ = [cita.strip('"“”') for cita in citas]
#     return citas_    
#     pakete_dict['citas'].append(citas1)