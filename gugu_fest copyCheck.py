import requests

# Kakao Map API 키
KAKAO_API_KEY = '89e49f0bccb5c561840496245d0ef1bb'

def test_kakao_api(address):
    url = f'https://dapi.kakao.com/v2/local/search/address.json?query={address}'
    headers = {'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("API 호출 성공!")
        print("응답 데이터:", data)
        return data
    else:
        print("API 호출 실패. 상태 코드:", response.status_code)
        return None

# 테스트할 주소
test_address = '서울특별시 강남구 테헤란로 123'

# API 테스트 호출
test_kakao_api(test_address)
