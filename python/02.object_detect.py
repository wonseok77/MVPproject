import requests  # HTTP 요청을 보내기 위한 requests 라이브러리 임포트
import os  # 운영 체제와 상호작용하기 위한 os 라이브러리 임포트
from dotenv import load_dotenv  # .env 파일에서 환경 변수를 로드하기 위한 dotenv 라이브러리 임포트
from PIL import Image, ImageDraw, ImageFont

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
    
# Object detect function
def object_detect(image_path):
    ENDPOINT_URL = ENDPOINT + "vision/v3.2/detect"

    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/octet-stream",
    }

    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None

# create bounding box function
def create_bounding_box(image_path, detection_data):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image file: {e}")
        return None
    
    draw = ImageDraw.Draw(image)

    for obj in detection_data.get("objects", []):
        rect = obj["rectangle"]
        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]
        draw.rectangle([x, y, x + w, y + h], outline="red", width=2)

        label = obj["object"]
        draw.text((x, y), obj["object"], fill="red", width = 2 )

    # 폰트 설정
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
        
    # Save the modified image
    parts = image_path.rsplit('.', 1)

    if len(parts) == 2:
        output_path = f"{parts[0]}_annotated.{parts[1]}"
    else:
        output_path = f"{image_path}_annotated"
    
    image.save(output_path)
    print(f"Annotated image saved as {output_path}")
    image.show()

# OCR function
def ocr_image(image_path):
    ENDPOINT_URL = ENDPOINT + "vision/v3.2/ocr"

    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/octet-stream",
    }

    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None

    response = requests.post(ENDPOINT_URL, headers=headers, data=image_data)
    if response.status_code == 200:
        ocr_result = response.json()
        return ocr_result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    # 사용자로부터 이미지 파일 경로 입력 받기
    image_path = input("Enter the path to the image file: ")

    print("1. Analyze Image")
    print("2. Object Detect")
    choice = input("Choose an option (1 or 2): ")

    if choice == '1':
        # 이미지 분석 함수 호출
        result = analyze_image(image_path)
    elif choice == '2':
        # 객체 감지 함수 호출
        result = object_detect(image_path)
        if result:
            # 객체 감지 결과에서 바운딩 박스 생성
            create_bounding_box(image_path, result)
        else:
            print("No objects detected or error occurred.")
    else:
        print("Invalid choice. Please select 1 or 2.")
        return

    # 이미지 분석 함수 호출
    result = analyze_image(image_path)
    if result:
        # 분석 결과 출력
        print("Analysis Result:")
        print(result)

if __name__ == "__main__":
    # 메인 함수
    main()

