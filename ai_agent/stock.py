import os
from dotenv import load_dotenv
import requests

load_dotenv()
STOCK_WEBAPP_URL = os.getenv("STOCK_WEBAPP_URL")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

sheet_dict = {
    "레드": ["RED"],
    "레드킹": ["RED"],
    "블루": ["BLUE"],
    "블루킹": ["BLUE"],
    "브라운": ["BROWN"],
    "브라운킹": ["BROWN"],
    "대게": ["SNOW"],
    "전체": ["RED", "BLUE", "BROWN", "SNOW"],
}

def stock_agent(user_msg):
    tokens = user_msg.split()

    if len(tokens) < 2:
        item = "전체"
    else:
        item = tokens[1]
    sheetNames = sheet_dict.get(item)
    
    if not sheetNames:
        return "❓ 해당 품목의 재고를 찾을 수 없습니다. 다음 중 하나를 선택해주세요: 레드, 블루, 브라운, 대게"

    try:
        response = requests.post(STOCK_WEBAPP_URL, json={"sheetNames": sheetNames, "secretToken": SECRET_TOKEN})
        data = response.json()
        status = data.get("status")
        status_code = data.get("statusCode")
        if status == "success":
            return data.get("stocks")
        elif status == "error" and status_code == 401:
            return "❌ 인증 실패: 허용되지 않은 접근입니다."
        else:
            return "⚠️ 재고 정보를 가져오는 데 실패했습니다. 나중에 다시 시도해주세요."
    except Exception as e:
        print(f"❌ 재고 조회 에러: {e}")
        return "⚠️ 재고 정보를 가져오는 중 오류가 발생했습니다. 나중에 다시 시도해주세요."
    