from telebot import TeleBot
import os
import sys
import http.server
import threading
from dotenv import load_dotenv

# ➕ 봇이 실행되는 현재 폴더 위치를 파이썬 시스템 경로에 강제로 등록합니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.balance import balance_agent
from ai_agent.packing import clear_packing_agent, set_packing_agent, set_size_agent
from ai_agent.stock import stock_agent

load_dotenv()  # 💡 .env 파일 환경 변수 로딩

# ==========================================
# [설정 영역]
# ==========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_IDS = [int(id) for id in os.getenv("ALLOWED_USER_IDS").split(",")]

bot = TeleBot(TELEGRAM_TOKEN)

# 📝 도움말 메시지 정의
HELP_TEXT = """
🤖 *킹크랩왕 AI 에이전트 허브 도움말*

사장님과 승인된 직원분들만 사용할 수 있는 비서 봇입니다. 
문장에 아래 키워드를 포함하여 명령해 주세요!

⚙️ *사용 가능한 주요 명령어:*
• 🔄 *리셋/초기화*: 포장 페이지 초기화 \n(예: 리셋 1)
• 📦 *준비/세팅*: 포장 페이지 준비 \n(예: 준비 1 ST 10)
• 📏 *사이즈*: 포장 페이지 사이즈 세팅 \n(예: 사이즈 1 1.5 10)
• 🦀 *재고*: 상품 재고 확인 (예: 재고 레드)
• 💰 *잔액*: 거래처별 잔액 조회

💡 *팁:* '도움말'이나 'help'를 입력하시면 언제든 이 설명서를 다시 볼 수 있습니다.
"""

# ==========================================
# [입구] 텔레그램 핸들러
# ==========================================
@bot.message_handler(func=lambda message: True)
def handle_incoming_message(message):
    user_msg = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    # 💡 [핵심 문지기]
    if user_id not in ALLOWED_USER_IDS:
        print(f"🚨 미승인 사용자 접근 차단 (ID: {user_id})")
        bot.send_message(chat_id, "❌ 이 봇을 사용할 권한이 없습니다.")
        return

    try:
        # 도움말 감지
        if user_msg in ["/start", "/help", "도움말", "help"]:
            bot.send_message(chat_id, HELP_TEXT, parse_mode="Markdown")
            return

        # 일반 명령어 진행
        bot.send_message(chat_id, f"🤖 요청하신 작업을 수행중입니다...")

        if "리셋" in user_msg or "초기화" in user_msg:
            response = clear_packing_agent(user_msg)
        elif "세팅" in user_msg or "준비" in user_msg:
            response = set_packing_agent(user_msg)
        elif "사이즈" in user_msg:
            response = set_size_agent(user_msg)
        elif "재고" in user_msg:
            response = stock_agent(user_msg)
        elif "잔액" in user_msg:
            response = balance_agent(user_msg)
        else:
            response = "❓ 명령을 이해하지 못했습니다.\n'리셋', '초기화', '세팅', '준비', '재고', '잔액' 등의 키워드를 포함하시거나, 자세한 설명은 '도움말'이나 'help'를 입력해 주세요."

    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        response = "⚠️ 명령 처리 중 오류가 발생했습니다. 다시 시도해 주세요."

    bot.send_message(chat_id, response)


# ========================================================
# 🛠️ [Render 포트 에러 해결용] 가짜 웹 서버 실행 영역
# ========================================================
def run_dummy_server():
    # 💡 핵심: Render가 할당하는 환경변수 'PORT'를 가져옵니다. 
    # (명시적으로 '0.0.0.0'을 사용하여 모든 외부 접속을 안전하게 허용합니다)
    port = int(os.environ.get("PORT", 10000))
    server_address = ('0.0.0.0', port) 

    class DummyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            # UptimeRobot이 찔러볼 때 정상(200 OK) 응답을 줍니다.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Bot is Running Safely!")

        def do_HEAD(self):
            # UptimeRobot이 살짝 찔러만 볼 때(HEAD)도 정상이라고 대답해 주는 코드
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def log_message(self, format, *args):
            # 무의미한 접속 로그가 Render 로그창을 도배하지 않도록 숨깁니다.
            pass

    httpd = http.server.HTTPServer(server_address, DummyHandler)
    print(f"✨ Render용 자동 매칭 포트({port}) 활성화 완료!")
    httpd.serve_forever()

# 3. 프로그램 시작점
if __name__ == "__main__":
    # 가짜 웹 서버를 백그라운드 스레드로 실행
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # 원래 하던 텔레그램 메시지 감시 시작
    print("🤖 킹크랩왕 AI 에이전트 허브가 가동되었습니다. 텔레그램 명령 대기 중...")
    bot.infinity_polling()
