# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from googletrans import Translator
import pdfkit
import requests

#html_english=Translator.translate('https://googleapis.dev/python/translation/latest/client.html', target_language='en', format_='html')

def get_html(_url):
    try:
        result = requests.get(_url)
        result.raise_for_status()
        return result.text
    except(requests.RequestException, ValueError):
        print('Server error')
        return False

drain_url = 'https://googleapis.dev/python/translation/latest/client.html'
drain_html = get_html(drain_url)

#source_html=Translator.translate(text= drain_html, target_language='ru', format_='html')

print('HELLO')
print(drain_html)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
