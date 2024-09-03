# 멍매니저 보호자 BE
## 서비스 소개
- 멍매니저는 강아지 유치원 사장님의 일정/등원 관리를 효율적으로 돕기 위한 서비스입니다.
- 해당 저장소는 사장님과 보호자 시스템으로 분리된 시스템 중 보호자 시스템에 해당합니다.
<br>

<img src="https://github.com/user-attachments/assets/9d88425a-0c9a-467f-82fd-cf0939ff9fcb" alt="1" width="600"/><br>
<img src="https://github.com/user-attachments/assets/450e2bbc-c971-4b49-9b3e-6623f340c30c" alt="2" width="600"/><br>
<img src="https://github.com/user-attachments/assets/2790ab44-79ff-435d-a6ae-dc4993af6074" alt="3" width="600"/><br>
<img src="https://github.com/user-attachments/assets/b7c1be18-69e2-4a21-bd07-75904c5a7267" alt="4" width="600"/><br>
<img src="https://github.com/user-attachments/assets/4578aca9-9892-4a76-af37-ec6160123cf1" alt="5" width="600"/><br>
<img src="https://github.com/user-attachments/assets/c81737fc-d0ea-49a4-a58d-8b53a09864a6" alt="6" width="600"/><br>
<img src="https://github.com/user-attachments/assets/ebe2111b-f420-49db-8aad-81e5b66e285a" alt="7" width="600"/><br>
<img src="https://github.com/user-attachments/assets/1888e944-a0ea-447f-869f-562577b0eae1" alt="8" width="600"/><br>
<img src="https://github.com/user-attachments/assets/619d1bed-c71a-438f-8be5-4f90b6feedd1" alt="9" width="600"/><br>


## 기술 스택
- Language: Python 3.11
- Backend: Django 5.0, Django Rest Framework, Celery, Celery-beats 
- DB: Postgresql16.0, PostGis
- Infra: AWS, Docker, Docker Compose, Nginx, Redis
- Management: Git, Github, Github Actions
- Swagger: drf-spectacular
- Monitoring: Sentry
- Code Style: black, isort, flake8, autoflake, bandit, mypy
- Communication: Slack, Notion

<br>

## 컨벤션 규칙
[그라운드 룰](https://hiallen.notion.site/Ground-Rule-c2a808cbf2fb479eaa56ded4fe617e7b?pvs=4)

[Git 브랜치 컨벤션](https://hiallen.notion.site/Git-Branch-6314f735522e441d830f774553b4a401?pvs=4)

[Git 커밋 컨벤션](https://hiallen.notion.site/Commit-Rule-001cdacdd0464530a02888bf8ca322bd?pvs=4)

[PR 및 이슈 컨벤션](https://hiallen.notion.site/PR-Issue-Bug-Convention-7f02a8337ea0441689f63be2d4c1ce71?pvs=4)

[주석 컨벤션](https://hiallen.notion.site/Comment-Convention-5dd546ebadaa4dacae4a2f2510574bfc?pvs=4)

[테스트 작성 컨벤션](https://hiallen.notion.site/5c7d9fbede43426fb466ea30151bc194?pvs=4)

- 프로젝트는 Layered 아키텍처로 진행하고 있습니다. 대략적인 구조 및 가이드는 아래 문서를 참조합니다.
  - [Django Style Guide](https://github.com/HackSoftware/Django-Styleguide)
  - [Django Style Guide Example](https://github.com/HackSoftware/Django-Styleguide-Example)
 
- 그외 팀 내에서 정한 규칙
  - [Selector / Service 네이밍 규칙](https://hiallen.notion.site/Selector-Service-632ba6c6a67d49e0ac7520484d74b343?pvs=4)
 
- 그외 읽어보면 좋을 글
  - [Django Layered 아키텍처](https://medium.com/athenaslab/django%EC%99%80-layered-architecture-%EC%82%AC%EC%9D%B4%EC%97%90%EC%84%9C-%ED%83%80%ED%98%91%EC%A0%90-%EC%B0%BE%EA%B8%B0-70769c13ef9d)

<br>

## 실행 방법
### env 구성
```
# Djnago Settings
SECRET_KEY="Django Secret Key" # Default:test
VERIFYING_KEY="Django JWT Verifying Key" # Default: test
SESSION_COOKIE_SECURE="Django Session Cookie Secure" # Default: True
HTTP_X_FORWARDED_PROTO="Django HTTP X Forwarded Proto" # Default: https
SECURE_SSL_REDIRECT="Secure SSL Redirect" # Default: True
SECURE_CONTENT_TYPE_NOSNIFF="Secure Content Type Nosniff" # Default: True

# Test Database
TEST_POSTGRESQL_DATABASE="Test Database Name" # Default: mung_manager
TEST_POSTGRESQL_USER="Test Database User" # Default: postgres
TEST_POSTGRESQL_PASSWORD="Test Database Password" # Default: password
TEST_POSTGRESQL_HOST="Test Database Host" # Default: localhost
TEST_POSTGRESQL_PORT="Test Database Port" # Default: 5432

# Local Database
LOCAL_POSTGRESQL_DATABASE="Local Database Name" # Default: mung_manager
LOCAL_POSTGRESQL_USER="Local Database User" # Default: postgres
LOCAL_POSTGRESQL_PASSWORD="Local Database Password" # Default: password
LOCAL_POSTGRESQL_HOST="Local Database Host" # Default: localhost
LOCAL_POSTGRESQL_PORT="Local Database Port" # Default: 5432

# Dev Database
DEV_POSTGRESQL_DATABASE="Dev Database Name" # Default: None
DEV_POSTGRESQL_USER="Dev Database User" # Default: None
DEV_POSTGRESQL_PASSWORD="Dev Database Password" # Default: None
DEV_POSTGRESQL_HOST="Dev Database Host" # Default: None
DEV_POSTGRESQL_PORT="Dev Database Port" # Default: None

# Django Debug Toolbar
DEBUG_TOOLBAR_ENABLED="Django Debug Toolbar Enabled" # Default: True

# Drf-yasg
SWAGGER_ENABLED="Drf-yasg Enabled" # Default: True

# Kakao API Key
KAKAO_SECRET_KEY="Kakao Secret Key" # Default: None
KAKAO_API_KEY="Kakao API Key" # Default: None

# CORS
DJANGO_BASE_BACKEND_URL="Django Base Backend Url" # Default: https://localhost:8000
DJANGO_BASE_FRONTEND_URL="Django Base Frontend Url" # Default: https://localhost:3000
DJANGO_CORS_ORIGIN_WHITELIS="Django Cors Origin Whitelist" # Default: https://localhost:3000

# Geo Local
GDAL_LIBRARY_PATH="Django GDAL Library Path" # Default: None
GEOS_LIBRARY_PATH="Django GEOS Library Path" # Default: None

# AWS S3
USE_S3="Use AWS S3" # Default: False
AWS_ACCESS_KEY_ID="AWS Access Key Id" # Default: None
AWS_SECRET_ACCESS_KEY="AWS Secret Access Key" # Default: None
AWS_STORAGE_BUCKET_NAME="AWS Storage Bucket Name" # Default: None
AWS_S3_REGION_NAME="AWS S3 Region Name" # Default: None
AWS_S3_URL="AWS S3 Url" # Default: None

```

### docker 환경

[docker 설치](https://docs.docker.com/engine/install/)
[docker compose 설치](https://docs.docker.com/compose/install/)

```bash
# 프로젝트 경로로 이동
docker login # 로그인을 진행

# docker compose 실행
docker compose up -d --build

# docker 재실행
docker compose restart <컨테이너 이름>
```

### 로컬 환경
```bash
# python 가상환경
python -m venv venv

# 가상환경 실행
source ./venv/bin/activate # mac
source ./venv/scripts/activate # window

# poetry 설치
pip install poetry

# 패키지 설치
poetry install

# 서버 실행
make start

# 데이터베이스 마이그레이트
make migrate
```
- 실행 전에 PostGIS를 사용하기에 [GEOS, GDAL](https://docs.djangoproject.com/en/5.0/ref/contrib/gis/install/geolibs/)를 설치해야합니다.
- PostgreSQL은 [PostGIS](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.PostGIS.html)를 설치해야합니다.

<br>

## 모듈 사용
- 저희는 코드 스타일을 맞추기 위해 코드 포맷팅을 사용하고 있습니다.

```bash
# 커밋 직전에 코드 스타일을 맞추기 위한 도구입니다.
pre-commit install

git add .
git commit

check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
check for added large files..............................................Passed
check for merge conflicts................................................Passed
flake8...................................................................Passed
black....................................................................Passed
autoflake................................................................Passed
isort....................................................................Passed
bandit...................................................................Passed
mypy.....................................................................Passed
```

- mypy를 개별 사용하고 싶다면 아래 명령어를 입력하십시오.
```bash
make mypy
```
<br>

## [ERD](https://www.erdcloud.com/d/KPTiwH5kMJdJbw3ne)
![멍매니저 공개용 ERD](https://github.com/user-attachments/assets/fb6616bd-93bd-4e0c-b86b-6ff8842300d0)
