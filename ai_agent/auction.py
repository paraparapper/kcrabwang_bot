import traceback
import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

from playwright.sync_api import sync_playwright

print("PLAYWRIGHT_BROWSERS_PATH =", os.getenv("PLAYWRIGHT_BROWSERS_PATH"))

def auction_agent(user_msg):
    """
    경매 관련 명령을 처리하는 에이전트 함수입니다.
    """

    tokens = user_msg.split()
    print(tokens)

    if len(tokens) < 2:
        crab_name = "왕게"  # 기본값
    else:
        crab_name = tokens[1].strip()  # 어종 이름 추출

        if crab_name not in ["왕게", "대게"]:
            return "❓ 지원하지 않는 어종입니다. '왕게' 또는 '대게'를 입력해주세요."
                

    # 날짜가 지정되지 않은 경우, 오늘 날짜를 기본값으로 사용
    from datetime import datetime
    today = datetime.now()
    year = today.year
    
    if len(tokens) <= 2:        
        # 10보다 작으면 앞에 0을 붙여서 두 자리로 만듭니다.
        if today.month < 10:
            month = f"0{today.month}"
        else:
            month = str(today.month)

        if today.day < 10:
            day = f"0{today.day}"
        else:
            day = str(today.day)

    else:
        if len(tokens[2]) == 1:
            month = f"0{tokens[2]}"
        else:
            month = tokens[2]

        if len(tokens[3]) == 1:
            day = f"0{tokens[3]}"
        else:
            day = tokens[3]          

    # Playwright를 사용하여 시세 조회
    message = f"📅 {year}-{month}-{day} {crab_name} 시세\n"
    message += "━━━━━━━━━━━\n"
    message += get_seafood_market_price(year, month, day, crab_name)

    return message

def get_seafood_market_price(year, month, day, crab_name):
    """
    year: 연도 (예: "2026")
    month: 월 (예: "08")
    day: 일 (예: "04")
    crab_name: "왕게" 또는 "대게"
    """

    browser = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )

            page = browser.new_page()

            # 1. 페이지 접속
            page.goto(
                "https://www.susansijang.co.kr/nsis/mim/info/mim9030",
                wait_until="networkidle"
            )

            # 페이지 로딩 확인
            page.wait_for_selector("select#searchYear")

            # 2. 연, 월, 일 선택
            page.select_option(
                "select#searchYear",
                value=str(year)
            )

            page.select_option(
                "select#searchMonth",
                value=str(month)
            )

            page.select_option(
                "select#searchDate",
                value=str(day)
            )

            # 3. 어종 선택
            page.select_option(
                "select#fishing_species",
                label=crab_name
            )

            # 4. 조회 버튼 클릭
            page.click("button#searchBtn")

            # 5. 결과 로딩 대기
            page.wait_for_timeout(2000)

            # 6. 결과 테이블 읽기
            rows = page.locator(
                "table tr"
            ).all_inner_texts()

            result = parse_market_data(
                rows,
                crab_name
            )

            return result

    except Exception:
        traceback.print_exc()
        return "❌ 시세 조회 중 오류가 발생했습니다."

    finally:
        if browser:
            browser.close()

def parse_market_data(raw_rows, crab_name):
    parsed_list = []

    message = ""
    for row in raw_rows:
        cols = row.split()
        
        if len(cols) >= 8 and crab_name in cols[0]:
            message += (
                        f"• {cols[0]} ({cols[1]})\n"
                        f"  - ⚖️  {cols[4]} kg\n"
                        f"  - 🔺 {cols[5]}원\n"
                        f"  - 🔻 {cols[6]}원\n"
                        f"  - 🔹 {cols[7]}원\n"
                        "\n"
                    )
            
    # 데이터가 없을 경우
    if message == "":
        message = f"{crab_name} 시세 조회 결과가 없습니다."
    
    return message

# --- 실행 예시 ---
if __name__ == "__main__":
    # 2026년 8월 4일 "왕게" 시세 조회
    response = auction_agent("경매 왕게 8 3")
    print(response)
    # results = get_seafood_market_price("2026", "08", "04", "왕게")
    # for data in results:
    #     print(data)
    
