import html  # HTML 엔티티 처리를 위해 추가
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"toptoon{current_date}.json"

# 웹 드라이버 초기화 및 페이지 로드
options = webdriver.ChromeOptions()
browser = webdriver.Chrome(options=options)
browser.get("https://toptoon.com/ranking#ranking1")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "weekly_list_wp"))
)

# 천천히 스크롤 다운
scroll_pause_time = 1  # 1초 대기
pixels_to_scroll = 200  # 한 번에 스크롤할 픽셀 수
max_time_limit = 60  # 전체 작업 시간 제한 (60초)
start_time = time.time()  # 작업 시작 시간

def scroll_down():
    """현재 위치에서 지정된 픽셀 수만큼 아래로 스크롤"""
    browser.execute_script(f"window.scrollBy(0, {pixels_to_scroll});")

while (time.time() - start_time) < max_time_limit:
    scroll_down()
    time.sleep(scroll_pause_time)
    # 스크롤 이동 후 새로운 높이를 계산
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == browser.execute_script("return window.pageYOffset + window.innerHeight"):
        break  # 페이지 끝에 도달

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 웹툰 타이틀 정보를 추출
webtoon_data = []
webtoon_list = soup.select('li.jsComicObj')  # CSS 선택자로 웹툰 리스트 선택

for webtoon in webtoon_list:
    title_tag = webtoon.select_one('.thumb_tit_text')
    image_box = webtoon.select_one('.thumbbox')
    view_count_tag = webtoon.select_one('.viewCountTxt')

    # 이미지 URL 추출하기 (style 속성에서 URL 파싱)
    if image_box and 'style' in image_box.attrs:
        style_content = image_box['style']
        if 'url(' in style_content:
            url_part = style_content.split('url(')[-1].split(')')[0].strip()
            image_url = html.unescape(url_part.strip('"'))
        else:
            image_url = "Image URL not found"
    else:
        image_url = "Image URL not found"

    title = title_tag.text.strip() if title_tag else "Title not found"
    view_count = view_count_tag.text.strip() if view_count_tag else "View count not found"

    webtoon_data.append({
        'title': title,
        'image_url': image_url,
        'view_count': view_count
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(webtoon_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"JSON 파일이 저장되었습니다: {filename}")
