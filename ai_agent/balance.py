import os
from dotenv import load_dotenv
import requests

load_dotenv()

BALANCE_WEBAPP_URL = os.getenv("BALANCE_WEBAPP_URL")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

def balance_agent(user_msg):
    response = requests.post(BALANCE_WEBAPP_URL, json={"secretToken": SECRET_TOKEN})
    data = response.json()
    status = data.get("status")
    if status == "success":
        return data.get("balances")
    elif status == "error" and data.get("statusCode") == 401:
        return "❌ 인증 실패: 허용되지 않은 접근입니다."
    else:
        return "⚠️ 잔액 정보를 가져오는 데 실패했습니다. 나중에 다시 시도해주세요."
    