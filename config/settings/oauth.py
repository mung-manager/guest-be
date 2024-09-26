from config.env import env
from config.django.base import SERVER_ENV

if SERVER_ENV == "config.django.prod":
    KAKAO_SECRET_KEY = env.str("KAKAO_PROD_SECRET_KEY", default=None)
    KAKAO_API_KEY = env.str("KAKAO_PROD_API_KEY", default=None)
else:
    KAKAO_SECRET_KEY = env.str("KAKAO_DEV_SECRET_KEY", default=None)
    KAKAO_API_KEY = env.str("KAKAO_DEV_API_KEY", default=None)

NAVER_CLOUD_ACCESS_KEY = env.str("NAVER_CLOUD_ACCESS_KEY", default=None)
NAVER_CLOUD_SECRET_KEY = env.str("NAVER_CLOUD_SECRET_KEY", default=None)
NAVER_CLOUD_SERVICE_ID = env.str("NAVER_CLOUD_SERVICE_ID", default=None)
NAVER_CLOUD_CHANNEL_ID = env.str("NAVER_CLOUD_CHANNEL_ID", default=None)
