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
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        if response.status_code == 200:
            return response.json().get("ip")
    except Exception as e:
        print_random_color_with_datetime(f"Error fetching IP: {e}")
    return None

def main():
    while True:
        load_dotenv(override=True)
        last_ip = os.getenv("last_ip")
        # GET CURRENT IP v4 ONLY
        current_ip = get_current_ip()

        if current_ip is None:
            print_random_color_with_datetime("⚠️ Không thể lấy IP hiện tại.")
            time.sleep(10)
            continue

        # if current_ip is ipv6, skip
        if ":" in current_ip:
            print_random_color_with_datetime("⚠️ IP hiện tại là IPv6, bỏ qua.")
            time.sleep(10)
            continue
        if current_ip != last_ip:
            print("IP changed, updating DNS...")
            username = os.getenv("username")
            password = os.getenv("password")
            domain_name = os.getenv("domain")

            print(f"Current IP: {current_ip}, Last IP: {last_ip}. Bắt đầu cập nhật...")
            login_result = API_123HOST.Login_Account(username, password)
            if not login_result:
                print_random_color_with_datetime("⚠️ Không thể đăng nhập. Thoát.")
                time.sleep(1080)  # wait 18 minutes
                continue
            access_token, _ = login_result
            set_key(".env", "access_token", access_token)
            os.environ["access_token"] = access_token

            try:
                time.sleep(2.7)  # wait 2.7 seconds before fetching domain info
                print("Bắt đầu lấy thông tin domain...")
                domain_id, ip_local = API_123HOST.GetInfoDomainByDomain(access_token, domain_name)
                # compare ip_local with current_ip
                if ip_local == current_ip:
                    print("IP in 123HOST is already up-to-date.")
                    set_key(".env", "last_ip", current_ip)
                    os.environ["last_ip"] = current_ip
                    time.sleep(10)
                    continue
                time.sleep(3.2)  # wait 3.2 seconds before updating
                print("Bắt đầu cập nhật DNS...")
                if API_123HOST.UpdateDNSDomain(access_token, domain_id, current_ip):
                    set_key(".env", "last_ip", current_ip)
                    os.environ["last_ip"] = current_ip
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
