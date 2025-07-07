import requests  # HTTP 요청을 보내기 위한 requests 라이브러리 임포트
import os  # 운영 체제와 상호작용하기 위한 os 라이브러리 임포트
from dotenv import load_dotenv  # .env 파일에서 환경 변수를 로드하기 위한 dotenv 라이브러리 임포트
# .env 파일에서 환경 변수 로드
load_dotenv()

SUBSCRIPTION_KEY = os.getenv("SUBSCRIPTION_KEY")  # Azure Computer Vision API 구독 키
ENDPOINT = os.getenv("ENDPOINT")  # Azure Computer Vision API 엔드포인트

def analyze_image(image_path):
    # 분석 요청을 보낼 API 엔드포인트 URL 생성
    ENDPOINT_URL = ENDPOINT + "vision/v3.2/analyze"

    # 분석에 사용할 시각적 특징 지정
    params = {"visualFeatures": "Categories,Description,Color"}
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,  # 인증을 위한 구독 키
        "Content-Type": "application/octet-stream",     # 바이너리 이미지 데이터 전송
    }

    try:
        # 이미지 파일을 바이너리 모드로 읽기
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        # 파일 읽기 실패 시 에러 메시지 출력 후 None 반환
        print(f"Error reading image file: {e}")
        return None
    
    # API에 POST 요청 보내기
    response = requests.post(ENDPOINT_URL, params=params, headers=headers, data=image_data)
    if response.status_code == 200:
        # 요청 성공 시 분석 결과(JSON) 반환
        analysis = response.json()
        return analysis
    else:
        # 요청 실패 시 에러 코드와 메시지 출력 후 None 반환
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
def main():
    # 사용자로부터 이미지 파일 경로 입력 받기
    image_path = input("Enter the path to the image file: ")

    # 이미지 분석 함수 호출
    result = analyze_image(image_path)
    if result:
        # 분석 결과 출력
        print("Analysis Result:")
        print(result["description"]["captions"][0]["text"])

if __name__ == "__main__":
    # 메인 함수
    main()

