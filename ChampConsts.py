__author__ = 'Spim'

import APIKey as KEY
import sys
import requests
import urllib
import os.path

#Get the list of all champions and associated info
response = requests.get("https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?champData=image&api_key=" + KEY.API_KEY)
if response.status_code != 200:
    sys.exit(1)

"""
CHAMP_ID dict will hold:
-ID as a key into champ name string
CHAMP_NAME dict will hold:
-Champ name string as a key into another dict, which holds:
--ID
--Champ Icon filename
"""
CHAMP_ID = dict()
CHAMP_NAME = dict()
champ_dict = response.json()['data']
for x in champ_dict:
    file_name = 'Icons\\' + champ_dict[x]['image']['full']
    if not os.path.exists(file_name):
        urllib.urlretrieve('http://ddragon.leagueoflegends.com/cdn/5.2.1/img/champion/' + champ_dict[x]['image']['full'], file_name)
    CHAMP_ID[champ_dict[x]['id']] = x
for x in sorted(CHAMP_ID, key=CHAMP_ID.get):
    CHAMP_NAME[CHAMP_ID[x]] = {
        'ID': x,
        'Icon': 'Icons\\' + CHAMP_ID[x] + '.png'
    }
