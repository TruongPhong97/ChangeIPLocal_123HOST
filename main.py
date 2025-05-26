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

def refresh_and_update_tokens(refresh_token: str):
    try:
        access_token, new_refresh_token = API_123HOST.Refresh_Token(refresh_token)
        set_key(".env", "access_token", access_token)
        set_key(".env", "refresh_token", new_refresh_token)
        print_random_color_with_datetime("✅ Token refreshed successfully")
        return access_token, new_refresh_token
    except Exception as e:
        print_random_color_with_datetime(f"❌ Failed to refresh token: {e}")
        traceback.print_exc()
        return None, refresh_token

def main():
    load_dotenv()
    access_token = os.getenv("access_token")
    refresh_token = os.getenv("refresh_token")
    domain_name = os.getenv("domain")

    # Làm mới token ban đầu
    access_token, refresh_token = refresh_and_update_tokens(refresh_token)
    if not access_token:
        print_random_color_with_datetime("⚠️ Không thể lấy access_token ban đầu. Thoát.")
        return

    # Lấy domain_id và IP local
    try:
        domain_id, ip_local = API_123HOST.GetInfoDomainByDomain(access_token, domain_name)
    except Exception as e:
        print_random_color_with_datetime(f"❌ Lỗi khi lấy domain_id ban đầu: {e}")
        traceback.print_exc()
        ip_local = None

    while True:
        try:
            current_ip = get_current_ip()

            if current_ip is None:
                print_random_color_with_datetime("⚠️ Không thể lấy IP hiện tại.")
                time.sleep(10)
                continue

            if ip_local != current_ip:
                print_random_color_with_datetime("🔁 Phát hiện thay đổi IP")
                print_random_color_with_datetime(f"🌐 IP mới: {current_ip}")
                print_random_color_with_datetime(f"🧠 IP cũ: {ip_local}")
                print_random_color_with_datetime(f"🔐 Access Token: {access_token}")

                try:
                    domain_id, _ = API_123HOST.GetInfoDomainByDomain(access_token, domain_name)
                    if API_123HOST.UpdateDNSDomain(access_token, domain_id, current_ip):
                        print_random_color_with_datetime("✅ Cập nhật DNS thành công!")
                        ip_local = current_ip
                    else:
                        print_random_color_with_datetime("❌ Cập nhật DNS thất bại.")
                except Exception as e:
                    print_random_color_with_datetime(f"❌ Lỗi khi cập nhật DNS: {e}")
                    traceback.print_exc()

            else:
                print_random_color_with_datetime("✔️ IP không thay đổi")

        except Exception as e:
            print_random_color_with_datetime(f"❌ Lỗi không xác định: {e}")
            traceback.print_exc()

        # Luôn đảm bảo nếu lỗi thì thử refresh token
        try:
            info_account = API_123HOST.GetInfoAccount(access_token)
            if info_account is None:
                print_random_color_with_datetime("⚠️ Token đã hết hạn hoặc không hợp lệ.")
                print_random_color_with_datetime("⚠️ Không thể lấy thông tin tài khoản. Thử làm mới token.")
                access_token, refresh_token = refresh_and_update_tokens(refresh_token)
            else:
                print_random_color_with_datetime(f"✔️ Token vẫn đang hoạt động, tiếp tục kiểm tra ...")
        except Exception as e:
            print_random_color_with_datetime(f"❌ Lỗi khi làm mới token: {e}")
            traceback.print_exc()

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
