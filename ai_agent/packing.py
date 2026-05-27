import requests
import os
from dotenv import load_dotenv

load_dotenv()  # 💡 이 한 줄이 .env 파일에 있는 비밀번호를 알아서 환경 변수로 로딩해 줍니다!
PACKING_WEBAPP_URL = os.getenv("PACKING_WEBAPP_URL")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
PACKING_NAMES = ["포장1", "포장2", "포장3", "포장4", "포장5", "포장6"]
PACKING = '포장'

def clear_packing_agent(user_msg):
    tokens = user_msg.split()

    if len(tokens) < 2:
        return "❓ 초기화 명령 형식이 올바르지 않습니다. 예: '리셋 1', '초기화 2', '리셋 1~3'"
    
    packing_number = tokens[1].strip()  # '포장' 제거 후 숫자만 추출
    if '~' in packing_number:
        start, end = packing_number.split('~')
        packing_names = [f"{PACKING}{i}" for i in range(int(start), int(end) + 1)]
    elif '-' in packing_number:
        start, end = packing_number.split('-')
        packing_names = [f"{PACKING}{i}" for i in range(int(start), int(end) + 1)]
    elif ',' in packing_number:
        numbers = packing_number.split(',')
        packing_names = [f"{PACKING}{num.strip()}" for num in numbers]
    else:
        packing_names = [f"{PACKING}{packing_number}"]

    valid_packing_names = [name for name in packing_names if name in PACKING_NAMES]
    if not valid_packing_names:
        return f"❓ 유효한 포장 이름이 없습니다. 다음 중 하나를 선택해주세요: {', '.join(PACKING_NAMES)}"
    print(valid_packing_names)
    try:
        response = requests.post(PACKING_WEBAPP_URL, json={"action": "clear", "targetList": valid_packing_names, "secretToken": SECRET_TOKEN})
        data = response.json()
        print(data)
        status = data.get("status")
        if status == "clear success":
            return f"✅ {', '.join(valid_packing_names)} 스프레드시트를 성공적으로 초기화했습니다! 📊"
        else:
            return "⚠️ 초기화에 실패했습니다. 나중에 다시 시도해주세요."
        
    except Exception as e:
        print(f"❌ 초기화 에러: {e}")
        return "⚠️ 초기화 중 오류가 발생했습니다. 나중에 다시 시도해주세요."


def set_packing_agent(user_msg):
    tokens = user_msg.split()
    if len(tokens) < 4:
        return "❓ 세팅 명령 형식이 올바르지 않습니다. 예: '준비 1 ST 10'"
    
    packing_name = PACKING + tokens[1]
    consignee = tokens[2].strip().upper()
    if consignee == '64':
        consignee = '6498779'
    pack_count = tokens[3].strip()

    response = requests.post(PACKING_WEBAPP_URL, json={"action": "set", "targetList": [packing_name], "secretToken": SECRET_TOKEN, "consignee": consignee, "packCount": pack_count})
    data = response.json()
    status = data.get("status")
    if status == "set success":
        return f"✅ {packing_name}에 '{consignee}'로 {pack_count}개 세팅 완료! 📦"
    else:
        return "⚠️ 세팅에 실패했습니다. 나중에 다시 시도해주세요." 
    
def set_size_agent(user_msg):
    tokens = user_msg.split()
    if len(tokens) < 4:
        return "❓ 사이즈 명령 형식이 올바르지 않습니다. 예: '사이즈 1(포장페이지) 1.5(사이즈) 10(개수)'"
    
    packing_name = PACKING + tokens[1]
    size_ranges = []
    pack_counts = []

    for i in range(2, min(len(tokens), 20), 2):
        if i + 1 >= len(tokens):
            break
        size_ranges.append(tokens[i].strip().upper())
        pack_counts.append(tokens[i + 1].strip())

    print(f"사이즈: {size_ranges}, 개수: {pack_counts}")

    response = requests.post(PACKING_WEBAPP_URL, json={"action": "set_size", "targetList": [packing_name], "secretToken": SECRET_TOKEN, "sizeRanges": size_ranges, "packCounts": pack_counts})
    data = response.json()
    status = data.get("status")
    if status == "set_size success":
        return f"✅ {packing_name}에 사이즈 '{size_ranges}'로 {pack_counts}개 세팅 완료! 📏"
    else:
        return "⚠️ 사이즈 세팅에 실패했습니다. 나중에 다시 시도해주세요."
