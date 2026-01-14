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

def UpdateDNSDomain(access_token, domain_id, new_ip, old_ip=None):
    """Update all A records for a domain that currently have content == old_ip.
    If old_ip is None, update any A record whose content != new_ip.
    Returns True if at least one update succeeded and no fatal errors occurred.
    """
    content_info = GetInfoDomainByID(access_token, domain_id)
    if content_info is None or "records" not in content_info:
        print(f"No DNS records found for domain_id={domain_id}")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}
    any_updated = False
    for record in content_info["records"]:
        try:
            record_type = record.get("type", {}).get("0")
            record_id = record.get("id")
            record_content = record.get("content")
            if record_type != "A":
                continue
            # decide whether to update this record
            if old_ip is not None:
                should_update = (record_content == old_ip) and (record_content != new_ip)
            else:
                should_update = (record_content != new_ip)

            if not should_update:
                continue

            jsonData = {
                "name": record.get("name", "@"),
                "type": "A",
                "priority": record.get("priority") or "",
                "content": new_ip
            }
            put_url = f"https://client.123host.vn/api/domain/{domain_id}/dns/{record_id}"
            resp = _request.put(put_url, json=jsonData, headers=headers)
            if resp.status_code == 200:
                print(f"Updated record id={record_id} name={jsonData['name']} -> {new_ip}")
                any_updated = True
            else:
                print(f"Failed to update record id={record_id}:", resp.status_code, resp.text)
                if resp.status_code == 429 or "rate limited" in (resp.text or "").lower():
                    print("Rate limited by Cloudflare. Waiting 18 minutes before retrying...")
                    time.sleep(1080)
                    return False
        except Exception as e:
            print(f"Exception updating record {record}: {e}")
    return any_updated
