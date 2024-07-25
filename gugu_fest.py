from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Selenium 웹드라이버 설정
options = Options()
options.add_experimental_option("detach", True)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options, service=service)

# URL 설정
base_url = 'https://mypethospitals.com/%EB%8F%99%EB%AC%BC%EB%B3%91%EC%9B%90-%EA%B2%80%EC%83%89%ED%95%98%EA%B8%B0'

# 모든 병원 정보를 저장할 리스트
all_names = []
all_tels = []
all_locations = []
all_etc = []

# 페이지 넘기기 및 데이터 추출
page_number = 1
while True:
    url = f'{base_url}/?type=place&pg={page_number}&sort=top-rated#google_vignette'
    driver.get(url)
    
    # 페이지 로드 대기 (5초)
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
        location = location_i_tag.find_next_sibling(string=True) if location_i_tag else '정보 없음'
    
        # 전화번호
        tel_i_tag = element.find('i', class_='icon-phone-outgoing sm-icon')
        tel = tel_i_tag.find_next_sibling(string=True) if tel_i_tag else '정보 없음'
    
        # 기타 정보
        etc_i_tag = element.find('i', class_='fa fa-hashtag sm-icon')
        etc = etc_i_tag.find_next_sibling(string=True) if etc_i_tag else '정보 없음'

        # 리스트에 추가
        all_names.append(name.text.strip() if name else '정보 없음')
        all_locations.append(location.strip() if location else '정보 없음')
        all_tels.append(tel.strip() if tel else '정보 없음')
        all_etc.append(etc.strip() if etc else '정보 없음')


    # 다음 페이지로 이동
    page_number += 1

driver.quit()

# 데이터 출력
for i in range(len(all_names)):
    print(f'이름: {all_names[i]}')
    print(f'주소: {all_locations[i]}')
    print(f'전화번호: {all_tels[i]}')
    print(f'기타: {all_etc[i]}')
    print('=' * 100)




