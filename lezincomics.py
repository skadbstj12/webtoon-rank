from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

# Chrome 옵션 설정
options = Options()
options.add_argument('--headless')  # headless 모드 활성화
options.add_argument('--no-sandbox')  # 샌드박스 모드 비활성화
options.add_argument('--disable-dev-shm-usage')  # /dev/shm 사용 제한

# Chrome 드라이버 서비스 설정
service = ChromeService(ChromeDriverManager().install())

# 드라이버 초기화
driver = webdriver.Chrome(service=service, options=options)

# 웹 드라이브를 설정하여 페이지에 접근
driver.get("https://bufftoon.plaync.com/tag/ranking?currentType=webtoon")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "width-box"))
)

# 천천히 스크롤 다운
scroll_pause_time = 1  # 1초 대기
pixels_to_scroll = 200  # 한 번에 스크롤할 픽셀 수
max_time_limit = 40  # 전체 작업 시간 제한 (40초)
start_time = time.time()  # 작업 시작 시간

while (time.time() - start_time) < max_time_limit:
    old_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollBy(0, {pixels_to_scroll});")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == old_height:
        break  # 페이지 끝에 도달

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"bufftoon_{current_date}.json"

html_source_updated = driver.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
webtoon_data = []
items = soup.select(".split-item")
for item in items:
    rank = item.select_one(".rank").text.strip() if item.select_one(".rank") else "Rank not found"
    title = item.select_one(".title .text").text.strip() if item.select_one(".title .text") else "Title not found"
    image_tag = item.select_one("img")
    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "Image URL not found"

    webtoon_data.append({
        "rank": rank,
        "title": title,
        "imageURL": image_url
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(webtoon_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
driver.quit()
