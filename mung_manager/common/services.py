from typing import Any, Dict, List, Tuple

from django.db import models
from django.utils import timezone

from mung_manager.common.types import DjangoModelType


def update_model(
    *,
    instance: DjangoModelType,
    fields: List[str],
    data: Dict[str, Any],
    auto_updated_at=True,
) -> Tuple[DjangoModelType, bool]:
    """앱 내부 업데이트 서비스에서 재사용할 수 있도록 만들어졌습니다.

    예를 들어:

    def update_user(*, user: User, data) -> User:
        fields = ['first_name', 'last_name']
        user, has_updated = model_update(instance=user, fields=fields, data=data)

        // 여기서 사용자와 관련된 다른 작업을 수행합니다.

        return user

    Return value: 다음과 같은 요소를 갖는 튜플입니다.
        1. 업데이트한 인스턴스
        2. 업데이트를 수행했는지 여부를 나타내는 부울 값

    몇 가지 중요한 사항:
        - `fields`에 있는 키만 `data`에서 가져옵니다.
        - `fields`에 있는 것 중 `data`에 없는 것은 건너뜁니다.
        - `fields`의 모든 값이 실제로 인스턴스의 필드임을 검증합니다.
        - `fields`는 m2m 필드를 지원할 수 있으며, 이는 인스턴스의 업데이트 후에 처리됩니다.
        - `auto_updated_at`이 True인 경우, 현재 시간으로 `updated_at`을 업데이트합니다.
    """
    has_updated = False
    m2m_data = {}
    update_fields = []

    model_fields = {field.name: field for field in instance._meta.get_fields()}

    for field in fields:
        # 실제 데이터에 필드가 없으면 건너뜀
        if field not in data:
            continue

        # 필드가 실제 모델 필드가 아닌 경우 오류를 발생
        model_field = model_fields.get(field)

        assert model_field is not None, f"{field} is not part of {instance.__class__.__name__} fields."

        # m2m 필드가 있는 경우, 다르게 처리
        if isinstance(model_field, models.ManyToManyField):
            m2m_data[field] = data[field]
            continue

        if getattr(instance, field) != data[field]:
            has_updated = True
            update_fields.append(field)
            setattr(instance, field, data[field])

    # 실제 변경된 필드가 있는 경우에만 업데이트를 수행
    if has_updated:
        if auto_updated_at:
            # 모델에 updated_at 필드가 있고 값이 제공되지 않은 경우에만 처리
            if "updated_at" in model_fields and "updated_at" not in update_fields:
                update_fields.append("updated_at")
                instance.updated_at = timezone.now()  # type: ignore

        # 업데이트해야 할 필드만 업데이트
        instance.save(update_fields=update_fields)

    for field_name, value in m2m_data.items():
        related_manager = getattr(instance, field_name)
        related_manager.set(value)

        # m2m 관계만 업데이트가 되었어도 업데이트 여부 True
        has_updated = True

    return instance, has_updated
