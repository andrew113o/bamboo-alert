import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "7986163513:AAFGpC98-IYEM3nYneyv7igFMCONDhQpU20"
CHAT_ID = "8850473772"

# 감시할 목표 조건
TARGET_DATES = ["10-09", "10-10", "10-17", "10-24", "10-31", "10/09", "10/10", "10/17", "10/24", "10/31"]
TARGET_ROOMS = ["트레일러1", "트레일러2", "트레일러3", "트레일러하우스1", "트레일러하우스2", "트레일러하우스3", "롯지4", "롯지5", "롯지6"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

def check_bamboo_reservation():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = "https://bamboosound.co.kr/reservation.php"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # iframe(외부 예약 연동창) 구조 감지
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            target_url = iframe.get("src")
            if not target_url.startswith("http"):
                target_url = "https://bamboosound.co.kr/" + target_url.lstrip("/")
            response = requests.get(target_url, headers=headers, timeout=15)
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, "html.parser")

        page_text = soup.get_text()
        
        # 예약 가능 여부 탐지 (사이트 문구 패턴 파악)
        available_found = []
        for d in TARGET_DATES:
            if d in page_text:
                for r in TARGET_ROOMS:
                    if r in page_text and ("예약가능" in page_text or "예약하기" in page_text):
                        available_found.append(f"[{d}] {r}")

        if available_found:
            msg = f"🔔 <b>[밤부사운드 빈자리 발견!]</b>\n\n" + "\n".join(available_found) + f"\n\n👉 바로가기: {url}"
            send_telegram(msg)
            print("빈자리 발견 및 알림 발송 완료!")
        else:
            print("예약 가능한 자리가 없거나 동적 스크립트로 로드 중입니다.")
            
    except Exception as e:
        print(f"체크 중 오류 발생: {e}")

if __name__ == "__main__":
    check_bamboo_reservation()
