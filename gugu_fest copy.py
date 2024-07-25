'''
[ 1단계 수집시스템 ] 조별로 통닭 & 커피 프랜차이즈 중 하나를 선택
웹페이지에서 매장명,전화번호,주소를 크롤링하여
DB에도 저장하기
( 오라클 or mariadb or mysql )
-----------------------------------
매장명 | 전화번호 | 주소 | 위도 | 경도
name  | tel    | addr | latitude | longitude
가산 | 02-2222 | 신촌동 |    |
'''
'''
[ 2단계 저장시스템 ] DB에 위도,경도 컬럼을 추가
주소를 입력하면 위도,경도를 알수 있는 웹API를 연결하여
해당 주소의 경도, 위도를 DB에 입력
ex) https://www.findlatlng.org/
ex) https://www.vworld.kr/dev/v4api.do
-----------------------------------
매장명 | 전화번호 | 주소 | 위도 | 경도
name  | tel    | addr | latitude | longitude
가산 | 02-2222 | 신촌동 | 11111.11 | 222222.22

* 해당 주소에 위도, 경도가 안 나올 수도 있음
'''
import pymysql, requests, folium, time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Kakao Map API 키
KAKAO_API_KEY = '89e49f0bccb5c561840496245d0ef1bb'

def get_lat_lng(address):
    url = f'https://dapi.kakao.com/v2/local/search/address.json?query={address}'
    headers = {'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
    response = requests.get(url, headers=headers)

    try:
        data = response.json()
        if 'documents' in data and data['documents']:
            latitude = data['documents'][0]['y']
            longitude = data['documents'][0]['x']
            return latitude, longitude
        else:
            print(f"No documents found for address: {address}")
            return None, None
    except Exception as e:
        print(f"Error fetching data for address: {address}, Error: {e}")
        return None, None

# 데이터베이스 연결 설정
conn = pymysql.connect(
    host='223.130.156.152',
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

# 크롤링한 데이터를 데이터베이스에 추가 또는 업데이트
for i in range(len(all_names)):
    latitude, longitude = get_lat_lng(all_locations[i])
    latitude = latitude if latitude else ''
    longitude = longitude if longitude else ''

    # 기존 데이터 확인
    cursor.execute("""
    SELECT * FROM test01 WHERE hospitalName=%s AND hospitalAddr=%s AND hospitalPhone=%s
    """, (all_names[i], all_locations[i], all_tels[i]))
    result = cursor.fetchone()

    if result:
        # 기존 데이터 업데이트
        cursor.execute("""
        UPDATE test01 
        SET hospitalTime=%s, hospitalSpecies=%s, hospitalType=%s, hospitalLati=%s, hospitalLongi=%s
        WHERE hospitalNo=%s
        """, ('', '', '', latitude, longitude, result[0]))
    else:
        # 새로운 데이터 삽입
        cursor.execute("""
        INSERT INTO test01 (hospitalName, hospitalAddr, hospitalPhone, hospitalTime, hospitalSpecies, hospitalType, hospitalLati, hospitalLongi)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (all_names[i], all_locations[i], all_tels[i], '', '', '', latitude, longitude))

# 변경사항 커밋 및 연결 종료
conn.commit()
conn.close()

# 데이터 출력
for i in range(len(all_names)):
    latitude, longitude = get_lat_lng(all_locations[i])
    latitude = latitude if latitude else ''
    longitude = longitude if longitude else ''
    print(f'이름: {all_names[i]}')
    print(f'주소: {all_locations[i]}')
    print(f'전화번호: {all_tels[i]}')
    print(f'기타: {all_etc[i]}')
    print(f'위도: {latitude}')
    print(f'경도: {longitude}')
    print('=' * 100)
