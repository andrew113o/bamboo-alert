import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "7986163513:AAFGpC98-IYEM3nYneyv7igFMCONDhQpU20"
CHAT_ID = "8850473772"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def check_booking():
    # 예약 확인 대상 사이트 조회 및 조건 검사
    url = "https://m.booking.naver.com"  # 네이버 예약 / 밤부사운드 예약 페이지 URL
    try:
        response = requests.get(url, timeout=10)
        # TODO: 타깃 날짜(10/9, 10, 17, 24, 31) 및 객실(트레일러1~3, 롯지4~6) 매칭 로직
        # 현재는 연동 테스트용 1회 확인 메시지 발송
        print("체크 완료")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_booking()
