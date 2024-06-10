from uuid import uuid4

from django.db import models


class DeletedRecord(models.Model):
    """이 클래스는 삭제된 레코드를 저장하기 위한 클래스입니다.
    https://brandur.org/soft-deletion
    """

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        serialize=False,
        default=uuid4,
        db_comment="삭제된 레코드 아이디",
    )
    original_table = models.CharField(max_length=256, db_comment="원본 테이블")
    original_id = models.IntegerField(db_comment="원본 아이디")
    data = models.JSONField(db_comment="원본 데이터")
    deleted_at = models.DateTimeField(auto_now_add=True, db_comment="삭제 시간")

    def __str__(self):
        return f"[{self.id}]: {self.original_table} - {self.original_id}"

    class Meta:
        db_table = "deleted_record"
        managed = False
