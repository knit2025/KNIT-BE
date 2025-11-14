# KNIT-BE
멋쟁이사자처럼 4호선톤 삼박이팀 KNIT BE 레포지토리입니다.

🧶 KNIT – 가족 소통 기반 미션·질문·일기 서비스 (Backend)

KNIT는 가족 구성원이 서로의 하루를 공유하고,
질문·미션·일기 작성 등을 통해 자연스럽게 대화를 형성하도록 돕는 서비스입니다.
본 레포지토리는 KNIT 서비스의 백엔드 API 서버 코드가 포함되어 있습니다.

⸻

📌 주요 기능

1. 가족 그룹 관리
- 초대 코드 기반 가족 구성
- 그룹 등록 / 참여 / 권한 관리

2. 오늘의 질문 (Today Question)
- 매일 생성되는 질문 조회
- 구성원별 답변 작성 및 열람

3. 일기 (Memory)
- 개인 일기 작성
- 날짜별 기록 조회

5. 커스텀 Q&A (Custom QA)
- 특정 가족 구성원 또는 전체에게 질문 작성
- 익명 여부 선택 가능
- 답변 저장 및 조회

6. 미션 (Mission)
- 가족 단위 미션 생성
- 구성원별 미션 상태 업데이트

⸻

🗂 주요 모델 구조 (요약)

User : belongs to Family

Family : code / status / created_at

TodayQuestion : question_text / date

TodayAnswer : user / question / content

Memory :  user / content / created_at

CustomQA : from_user / to_user(optional) / question / anonymous

Mission : family / template / is_completed


⸻

🛠 기술 스택
- Language: Python 3.12
- Framework: Django 5.2 / Django REST Framework (DRF)
- Auth: SimpleJWT (Access/Refresh Token)
- DB: PostgreSQL
- Deploy: Gunicorn + Nginx + AWS EC2 (Ubuntu)

⸻


🧪 로컬 실행 방법

1. Clone

git clone https://github.com/knit2025/KNIT-BE.git
cd KNIT-BE

2. 가상환경 생성 및 활성화

python3 -m venv venv
source venv/bin/activate

3. 패키지 설치

pip install -r requirements.txt

4. migrate & runserver

python manage.py migrate
python manage.py runserver


⸻

🚀 배포 방법 (EC2)

- git pull origin main
- sudo systemctl restart gunicorn
- sudo systemctl restart nginx
