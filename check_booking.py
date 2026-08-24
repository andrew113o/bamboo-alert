import os
import sys
import time
from datetime import datetime, timezone, timedelta
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

def check_once():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = "https://bamboosound.co.kr/reservation.php"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            target_url = iframe.get("src")
            if not target_url.startswith("http"):
                target_url = "https://bamboosound.co.kr/" + target_url.lstrip("/")
            response = requests.get(target_url, headers=headers, timeout=15)
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, "html.parser")

        page_text = soup.get_text()
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
            return True
        else:
            print("빈자리 없음 (감시 중...)")
            return False
            
    except Exception as e:
        print(f"체크 중 오류: {e}")
        return False

if __name__ == "__main__":
    # 한국 표준시(KST, UTC+9) 기준 계산
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst)
    expiry_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=kst)

    # 2026년 11월 1일 이후 만료 안내 발송 및 자동 종료
    if now_kst >= expiry_date:
        notice_msg = (
            "🏁 <b>[밤부사운드 10월 감시 종료 안내]</b>\n\n"
            "10월 예약 대상 기간이 만료되어 자동 감시가 완전히 종료되었습니다.\n\n"
            "<b>[정리 작업 안내]</b>\n"
            "1. <b>GitHub 정리</b>: GitHub 저장소(bamboo-alert) 삭제 또는 Actions 비활성화\n"
            "2. <b>텔레그램 정리</b>: 생성한 봇 방 나가기 또는 BotFather를 통한 봇 삭제\n\n"
            "정리 방법이 궁금하시면 아래 복사용 문구를 복사하여 AI에게 그대로 질문해 주세요:\n\n"
            "<code>밤부사운드 10월 예약 감시 프로그램이 종료되었습니다. GitHub 저장소(bamboo-alert) 삭제/비활성화 방법과 텔레그램 봇 정리 방법을 단계별로 안내해 주세요.</code>"
        )
        send_telegram(notice_msg)
        print("10월 감시 기간이 만료되어 안내 메시지 발송 후 종료합니다.")
        sys.exit(0)

    # 25분 동안 60초 간격 감시
    start_time = time.time()
    while time.time() - start_time < 25 * 60:
        found = check_once()
        if found:
            time.sleep(180)  # 빈자리 발견 시 3분 대기
        else:
            time.sleep(60)   # 미발견 시 1분 대기
