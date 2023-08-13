import requests


url = "http://mobywatel-monitoring-backend.pro.coi.gov.pl:9090/api/v1/query"


#Tworzyl Filip Kubasiewicz
#Skrypt wyciaga dane z prometheusa ktory chodzi w kontenerze
#Wykonuje go Nagios Epuap co 5 min a nastepnie przesyla na proxy miedzy zir a dmz i wrzuca na grafane dostepna dla ministra

import urllib.parse
import urllib.request
import json
import time
from datetime import datetime, timedelta

#Czas zrobiony na potrzeby czytania danych za dzis

# Ustalamy zakres czasu na dzis
start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# Konwersja na timestamp
start_timestamp = int(start_of_day.timestamp())
# Roznica miedzy aktualnym czasem a poczatkiem dnia w sekundach
time_difference = int(time.time()) - start_timestamp


#Query z podstawionymi sekundami
bebus = f'sum (increase(http_server_requests_seconds_count{{app=~"vehicle-service", uri=~"/mobile/api/vehicles/safe.*"}}[{time_difference}s]))'
deaktywacje_mobywatel = f'sum (increase(http_server_requests_seconds_count{{app=~"authentication-service", uri=~"/mobile/api/deactivation",method="DELETE"}}[{time_difference}s]))'
udane_uzycia_wk = f'sum by(status, uri, exception, method, app) (increase(http_server_requests_seconds_count{{app=~"wk-integrator-backend|back-system", uri=~".*idp.*",status="200"}}[{time_difference}s]))'
wydane_mdowody = f'sum (increase (mob_authentication_new_mobile_id_card_added_total{{}}[{time_difference}s]))'
logowania = f'sum (increase(http_server_requests_seconds_count{{app=~"authentication-service", uri=~"/mobile.*/jwt",method="POST"}}[{time_difference}s]))'

#Tabela z query
queries = [bebus,deaktywacje_mobywatel,udane_uzycia_wk,wydane_mdowody,logowania]
queries_name = ['bebus','deaktywacje_mobywatel','udane_uzycia_wk','wydane_mdowody','logowania']

#URL do promka
prom_url = 'http://mobywatel-monitoring-backend.pro.coi.gov.pl:9090/api/v1/query'

for query,name in zip(queries,queries_name):
    params = urllib.parse.urlencode({'query': query})
    full_url = f"{prom_url}?{params}"
    with urllib.request.urlopen(full_url) as response:
        if response.status == 200:
            data = response.read()
            json_data = json.loads(data)
            liczba = json_data['data']['result'][0]['value'][1]
            number = float(liczba)
            rounded_number = round(number)
            print(f"metrics,usluga=graf_mobywatel,rodzaj={name} ilosc={rounded_number}")

        else:
            print("Blad odczytu")
