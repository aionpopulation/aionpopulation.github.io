# check_empire.py
import requests, re
r = requests.get('https://aionempire.com/', headers={'User-Agent': 'Mozilla/5.0'})
idx = r.text.find('class="online"')
print(repr(r.text[idx:idx+200]))