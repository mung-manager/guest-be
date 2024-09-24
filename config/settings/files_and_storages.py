import os
from config.env import env, BASE_DIR

FILE_MAX_SIZE = env.int("FILE_MAX_SIZE", default=10485760)  # 10 MiB

AWS_S3_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME")

AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")
AWS_S3_URL = env("AWS_S3_URL")
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

# ==================================================================== #
#                  file system (static) config                         #
# ==================================================================== #
USE_S3 = env.bool("USE_S3", default=False)

STATIC_ROOT = os.path.join(BASE_DIR, "static")

if USE_S3:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3StaticStorage",
        },
    }

    AWS_LOCATION = "guest/static"
    STATIC_URL = f"{AWS_S3_URL}/{AWS_LOCATION}/"
else:
    STATIC_URL = "/guest/static/"
