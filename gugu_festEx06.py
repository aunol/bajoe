from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pymysql
import time

# 데이터베이스 연결 설정
conn = pymysql.connect(
    host='localhost',
    user='scott',
    password='tiger',
    db='0final',
    charset='utf8'
)
cursor = conn.cursor()

# 데이터베이스 테이블 생성 (이미 존재하는 경우는 무시)
cursor.execute("""
CREATE TABLE IF NOT EXISTS test01 (
    hospitalNo INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    hospitalName VARCHAR(100) NOT NULL,
    hospitalAddr VARCHAR(100) NOT NULL,
    hospitalPhone VARCHAR(100) NOT NULL,
    hospitalTime VARCHAR(100) NOT NULL,
    hospitalSpecies VARCHAR(100) NOT NULL,
    hospitalType VARCHAR(100) NOT NULL,
    hospitalLati VARCHAR(100) NOT NULL,
    hospitalLongi VARCHAR(100) NOT NULL
);
""")

# Selenium 웹드라이버 설정
options = Options()
options.add_experimental_option("detach", True)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options, service=service)

# URL 설정
base_url = 'https://mypethospitals.com/%eb%8f%99%eb%ac%bc%eb%b3%91%ec%9b%90-%ea%b2%80%ec%83%89%ed%95%98%ea%b8%b0/?type=place&available-animals=%25EA%25B3%25A0%25EC%2596%2591%25EC%259D%25B4&sort=top-rated'

# 모든 병원 정보를 저장할 리스트
all_names = []
all_tels = []
all_locations = []
all_etc = []

# 페이지 넘기기 및 데이터 추출
page_number = 1
while True:
    url = f'{base_url}&pg={page_number}'
    driver.get(url)
    
    # 페이지 로드 대기 (3초)
    time.sleep(3)
    
    try:
        # 페이지가 로드될 때까지 대기
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'grid-item')))
    except Exception as e:
        print("더 이상 페이지가 없습니다.", e)
        break

    # 페이지 소스 가져오기
    page_source = driver.page_source
    bs = BeautifulSoup(page_source, 'html.parser')

    # 모든 병원 정보를 포함하는 요소들을 찾습니다.
    hospital_elements = bs.select('.col-md-12.grid-item.hide-priority')

    if not hospital_elements:
        print("더 이상 병원 정보가 없습니다.")
        break

    # 각 요소에서 데이터를 추출합니다.
    for element in hospital_elements:
        # 병원이름
        name = element.select_one('h4')
    
        # 병원주소
        location_i_tag = element.find('i', class_='icon-location-pin-add-2 sm-icon')
        location = location_i_tag.find_next_sibling(string=True).strip() if location_i_tag else ''
    
        # 전화번호
        tel_i_tag = element.find('i', class_='icon-phone-outgoing sm-icon')
        tel = tel_i_tag.find_next_sibling(string=True).strip() if tel_i_tag else ''
    
        # 기타 정보
        etc_i_tag = element.find('i', class_='fa fa-hashtag sm-icon')
        etc = etc_i_tag.find_next_sibling(string=True).strip() if etc_i_tag else ''

        # 리스트에 추가
        all_names.append(name.text.strip() if name else '')
        all_locations.append(location if location else '')
        all_tels.append(tel if tel else '')
        all_etc.append(etc if etc else '')

    # 다음 페이지로 이동
    page_number += 1

driver.quit()

# 크롤링한 데이터를 데이터베이스에 업데이트
for i in range(len(all_names)):
    # 기존 데이터 확인
    cursor.execute("""
    SELECT hospitalSpecies FROM test01 WHERE hospitalName=%s
    """, (all_names[i],))
    result = cursor.fetchone()

    if result:
        current_species = result[0]
        if '고양이' not in current_species:
            new_species = current_species + '/고양이' if current_species else '고양이'
            cursor.execute("""
            UPDATE test01 
            SET hospitalSpecies=%s
            WHERE hospitalName=%s
            """, (new_species, all_names[i]))

# 변경사항 커밋 및 연결 종료
conn.commit()
conn.close()

# 데이터 출력
for i in range(len(all_names)):
    print(f'이름: {all_names[i]}')
    print(f'주소: {all_locations[i]}')
    print(f'전화번호: {all_tels[i]}')
    print(f'기타: {all_etc[i]}')
    print('=' * 100)
