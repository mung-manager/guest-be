from django.contrib.auth.models import (
    AbstractBaseUser,
    Group,
    Permission,
    PermissionsMixin,
)
from django.db import models

from mung_manager.authentication.managers import UserManager
from mung_manager.common.base.models import SimpleModel, TimeStampedModel


class User(AbstractBaseUser, TimeStampedModel, PermissionsMixin):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="user_id",
        serialize=False,
        db_comment="유저 아이디",
    )
    email = models.EmailField(unique=True, db_comment="이메일")
    social_id = models.CharField(max_length=64, unique=True, blank=True, db_comment="소셜 아이디")
    name = models.CharField(max_length=32, db_comment="이름")
    is_active = models.BooleanField(default=True, db_comment="활성 여부")
    is_deleted = models.BooleanField(default=False, db_comment="삭제 여부")
    is_admin = models.BooleanField(default=False, db_comment="관리자 여부")
    deleted_at = models.DateTimeField(blank=True, null=True, db_comment="삭제 일시")
    is_agree_privacy = models.BooleanField(default=True, db_comment="개인정보 동의 여부")
    is_agree_marketing = models.BooleanField(default=False, db_comment="마케팅 정보 수신 동의 여부")
    gender = models.CharField(max_length=1, blank=True, db_comment="성별")
    birth = models.DateField(blank=True, db_comment="생년월일")
    phone_number = models.CharField(max_length=16, blank=True, db_comment="전화번호")
    user_social_provider = models.ForeignKey(
        "UserSocialProvider",
        on_delete=models.CASCADE,
        related_name="users",
        db_comment="유저 소셜 제공자 아이디",
    )
    groups = models.ManyToManyField(
        Group,
        related_name="user_set",
        related_query_name="user",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions " "granted to each of their groups."
        ),
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="user_set",
        related_query_name="user",
        blank=True,
        help_text=("Specific permissions for this user."),
        verbose_name="user permissions",
    )

    objects = UserManager()  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone_number", "gender", "birth"]

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = "users"
        managed = False


class UserSocialProvider(SimpleModel):
    """
    email: 이메일 제공자
    kakao: 카카오 제공자
    """

    id = models.SmallAutoField(
        auto_created=True,
        primary_key=True,
        db_column="user_social_provider_id",
        serialize=False,
        db_comment="유저 소셜 제공자 아이디",
    )

    class Meta:
        db_table = "T_user_social_provider"
        managed = False
