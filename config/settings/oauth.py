from config.env import env

KAKAO_SECRET_KEY = env.str("KAKAO_SECRET_KEY", default=None)
KAKAO_API_KEY = env.str("KAKAO_API_KEY", default=None)
