import requests
import time

_request = requests.Session()
def Login_Account(username, password):
    jsonData = {
        "username": username,
        "password": password
    }
    response = _request.post("https://client.123host.vn/api/login", json=jsonData)
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
        time.sleep(2.2)  # wait 2.2 seconds before fetching domain info
        content_info = GetInfoDomainByID(access_token, id)
        ip_123Host = None
        if content_info is not None and "records" in content_info:
            for record in content_info["records"]:
                if record.get("name") == "@" and record.get("type", {}).get("0") == "A":
                    ip_123Host = record.get("content")
                    break
            return id, ip_123Host
        else:
            return id, None
    else:
        return None, None

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
        print(response.status_code, response.text)
        if response.status_code == 429 or "rate limited" in response.text.lower():
            print("Rate limited by Cloudflare. Waiting 18 minutes before retrying...")
            time.sleep(1080)  # wait 18 minutes
            return False
        return False
