from dotenv import load_dotenv, set_key
import API_123HOST
import os
import requests
import time
import random
import datetime

def print_random_color_with_datetime(message: str):
    colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Cyan", "Magenta", "Pink"]
    random_color = random.choice(colors)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

def Get_IP():
    response = requests.get("https://api.myip.com")
    if response.status_code == 200:
        return response.json()["ip"]
    else:
        return None

load_dotenv() 
accesss_token = os.getenv("access_token")
refresh_token = os.getenv("refresh_token")
accesss_token, refresh_token = API_123HOST.Refresh_Token(refresh_token)
set_key(".env", "access_token", accesss_token)
set_key(".env", "refresh_token", refresh_token)
print('access_token', accesss_token)
print('refresh_token', refresh_token)
domain_id, ip_web = API_123HOST.GetInfoDomainByDomain(accesss_token, os.getenv("domain"))

ip_local = ip_web
while True:
    accesss_token = os.getenv("access_token")
    try:
        load_dotenv()
        ip_new = Get_IP()
        if ip_new is not None and ip_local != ip_new:   
            print_random_color_with_datetime("IP change detected")
            print_random_color_with_datetime("IP change: " + ip_new)
            print_random_color_with_datetime("IP local: "+  ip_local)
            print_random_color_with_datetime("Access Token: " + accesss_token)  
            domain_id, ip_web = API_123HOST.GetInfoDomainByDomain(accesss_token, os.getenv("domain"))
            print_random_color_with_datetime("Domain ID: " + domain_id)
            if API_123HOST.UpdateDNSDomain(accesss_token, domain_id, ip_new):
                print_random_color_with_datetime("Update DNS Success")
            else:
                print_random_color_with_datetime("Update DNS Fail")
            domain_id, ip_local = API_123HOST.GetInfoDomainByDomain(accesss_token, os.getenv("domain"))
        else:
            print_random_color_with_datetime("IP not changed")
        time.sleep(10)
    except:
        accesss_token, refresh_token = API_123HOST.Refresh_Token(refresh_token)
        set_key(".env", "access_token", accesss_token)
        set_key(".env", "refresh_token", refresh_token)
