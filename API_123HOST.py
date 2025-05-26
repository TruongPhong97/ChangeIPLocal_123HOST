import requests

_request = requests.Session()
def Login_Account(username, password):
    jsonData = {
        "username": username,
        "password": password
    }
    response = _request.post("https://client.123host.vn/api/login", json=jsonData)
    if(response.status_code == 200):
        access_token = response.json()["token"]
        # set access_token to .env 
        return access_token
    else:
        return None

def Refresh_Token(refresh_token):
    jsonData = {
        "refresh_token": refresh_token
    }
    response = _request.post("https://client.123host.vn/api/token", json=jsonData)
    if(response.status_code == 200):
        access_token = response.json()["token"]
        refresh_token = response.json()["refresh"]
        # set access_token to .env 
        return access_token, refresh_token
    else:
        return None

def GetInfoDomainByDomain(access_token, domain):
    response = _request.get(f"https://client.123host.vn/api/domain/name/{domain}", headers={"Authorization": f"Bearer {access_token}"})
    if(response.status_code == 200):
        id = response.json()["domains"][0]["id"]
        content_info = GetInfoDomainByID(access_token, id)
        if(content_info != None):        
            ip_123Host = content_info["records"][4]["content"]
        return id, ip_123Host
    else:
        return None

def GetInfoDomainByID(access_token, domain_id):
    response = _request.get(f"https://client.123host.vn/api/domain/{domain_id}/dns", headers={"Authorization": f"Bearer {access_token}"})
    if(response.status_code == 200):
        return response.json()
    else:
        return None

def UpdateDNSDomain(access_token, domain_id, ip):
    jsonData = {
        "name": "@",
        "type": "A",
        "priority": "",
        "content": ip
    }
    response = _request.put(f"https://client.123host.vn/api/domain/{domain_id}/dns/4", json=jsonData, headers={"Authorization": f"Bearer {access_token}"})
    if(response.status_code == 200):
        print(response.json())
        return True
    else:
        return False