import django_filters

from mung_manager.customers.models import Customer


class CustomerFilter(django_filters.FilterSet):
    """이 클래스는 고객 필터링을 위한 클래스입니다.

    Attributes:
        customer_name (django_filters.CharFilter): 고객 이름 필터
        customer_phone_number (django_filters.CharFilter): 고객 전화번호 필터
        customer_pet_name (django_filters.CharFilter): 고객 반려동물 이름 필터
        is_active (django_filters.BooleanFilter): 고객 활성화 여부 필터
    """

    customer_name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    customer_phone_number = django_filters.CharFilter(field_name="phone_number", lookup_expr="icontains")
    customer_pet_name = django_filters.CharFilter(field_name="customer_pets__name", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Customer
        fields = [
            "customer_name",
            "customer_phone_number",
            "customer_pet_name",
            "is_active",
        ]
