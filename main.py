from telebot import TeleBot
import os
import sys  # ➕ 외부 서버 경로 인식을 위해 추가
from dotenv import load_dotenv

# ➕ 봇이 실행되는 현재 폴더 위치를 파이썬 시스템 경로에 강제로 등록합니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.balance import balance_agent
from ai_agent.packing import clear_packing_agent, set_packing_agent
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


def main():
    print("🚀 킹크랩왕 AI 에이전트 허브가 가동되었습니다. 텔레그램 명령 대기 중...")
    bot.infinity_polling()


if __name__ == "__main__":
    main()