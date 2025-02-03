from dotenv import load_dotenv
import API_123HOST
import os
import requests
import time

def Get_IP():
    response = requests.get("https://api.myip.com")
    if(response.status_code == 200):
        return response.json()["ip"]
    else:
        return None
    
accesss_token = os.getenv("access_token")
print("Access Token: ", accesss_token)  
domain_id, ip_web = API_123HOST.GetInfoDomainByDomain(accesss_token, os.getenv("domain"))

ip_local = ip_web
while(True):
    load_dotenv()
    ip_new = Get_IP()
    if ip_new != None and ip_local != ip_new:   
        print("IP change: ", ip_new)
        print("IP local: ", ip_local)
        print("Access Token: ", accesss_token)  
        domain_id, ip_web = API_123HOST.GetInfoDomainByDomain(accesss_token, os.getenv("domain"))
        print("Domain ID: ", domain_id)
        if(API_123HOST.UpdateDNSDomain(accesss_token, domain_id, ip_new)):
            print("Update DNS Success")
        else:
            print("Update DNS Fail")
        domain_id, ip_local = API_123HOST.GetInfoDomainByDomain(accesss_token, os.getenv("domain"))
    else:
        print("IP not change")
    time.sleep(10)