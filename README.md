# Scrapers de medios online
Estas son distintos scripts para scrapear medios de noticias de Argentina utilizando principalmente BeautifulSoup y ocasionalmente Selenium

## Medios
* Infobae
* Clarín
* La Nación
* Página12
* Perfil
* Ámbito Financiero
* TN
* Crónica
* La Voz del Interior
* La Capital

## **Requerimientos**

*  Python
*  Python Libraries: [`bs4`](https://pypi.org/project/bs4/), [`datetime`](https://pypi.org/project/DateTime/), [`pandas`](https://pandas.pydata.org/docs/getting_started/install.html), [`selenium`](https://pypi.org/project/selenium/), [`pytz`](https://pypi.org/project/pytz/), `re`, `unicodedata`

## **Cómo usar**

Cada código se ejecuta y crea un archivo _nombremedio_fecha_hora.csv_ con el nombre del medio, la fecha y la hora en que se ejecutó.

## **Output**

Cada archivo generado contiene la fecha, hora, texto de la noticia, identificador único (en su mayoría el link o un fragmento del mismo) y lista de citas (frases atribuidas a individuos entre comillas) de todas las noticias  de la _homepage_ del medio.
![image](https://github.com/Bardiego/scrap_medios_Argentina/assets/42683164/81c6fda1-ee0c-4fda-8394-14d90781ed01)
