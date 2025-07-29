from dotenv import load_dotenv, set_key
import API_123HOST
import os
import requests
import time
import random
import datetime
import traceback

def print_random_color_with_datetime(message: str):
    colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Cyan", "Magenta", "Pink"]
    color = random.choice(colors)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}][{color}] {message}")

def get_current_ip():
    try:
        response = requests.get("https://api.myip.com", timeout=10)
        if response.status_code == 200:
            return response.json().get("ip")
    except Exception as e:
        print_random_color_with_datetime(f"Error fetching IP: {e}")
    return None

def refresh_and_update_tokens(refresh_token):
    try:
        result = API_123HOST.Refresh_Token(refresh_token)
        if result is None:
            print_random_color_with_datetime("❌ Token refresh failed, trying login with username/password...")
            # Try login with username/password
            username = os.getenv("username")
            password = os.getenv("password")
            access_token, new_refresh_token = API_123HOST.Login_Account(username, password)
            if access_token and new_refresh_token:
                set_key(".env", "access_token", access_token)
                set_key(".env", "refresh_token", new_refresh_token)
                refresh_token = new_refresh_token  # Update refresh_token to the new one
                print_random_color_with_datetime("✅ Logged in and got new access_token")
                return access_token, refresh_token  # You may want to update refresh_token if API provides it
            else:
                print_random_color_with_datetime("❌ Login failed. Check your username/password.")
                return None, refresh_token
        access_token, new_refresh_token = result
        set_key(".env", "access_token", access_token)
        set_key(".env", "refresh_token", new_refresh_token)
        print_random_color_with_datetime("✅ Token refreshed successfully")
        return access_token, new_refresh_token
    except Exception as e:
        print_random_color_with_datetime(f"❌ Failed to refresh token: {e}")
        traceback.print_exc()
        return None, refresh_token

def main():
    while True:
        load_dotenv()
        last_ip = os.getenv("last_ip")
        current_ip = get_current_ip()

        if current_ip is None:
            print_random_color_with_datetime("⚠️ Không thể lấy IP hiện tại.")
            time.sleep(10)
            continue

        if current_ip != last_ip:
            print("IP changed, updating DNS...")
            access_token = os.getenv("access_token")
            refresh_token = os.getenv("refresh_token")
            domain_name = os.getenv("domain")

            access_token, refresh_token = refresh_and_update_tokens(refresh_token)
            if not access_token:
                print_random_color_with_datetime("⚠️ Không thể lấy access_token ban đầu. Thoát.")
                time.sleep(10)
                continue

            try:
                domain_id, ip_local = API_123HOST.GetInfoDomainByDomain(access_token, domain_name)
                if API_123HOST.UpdateDNSDomain(access_token, domain_id, current_ip):
                    set_key(".env", "last_ip", current_ip)
                    print_random_color_with_datetime("✅ Cập nhật DNS thành công!")
                else:
                    print_random_color_with_datetime("❌ Cập nhật DNS thất bại.")
            except Exception as e:
                print_random_color_with_datetime(f"❌ Lỗi khi cập nhật DNS: {e}")
                traceback.print_exc()
        else:
            print("IP unchanged, no update needed.")

        time.sleep(10)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as main_e:
            print_random_color_with_datetime(f"🔥 Lỗi nghiêm trọng ở cấp độ main: {main_e}")
            traceback.print_exc()
            print_random_color_with_datetime("🔁 Khởi động lại sau 10 giây...")
            time.sleep(10)
