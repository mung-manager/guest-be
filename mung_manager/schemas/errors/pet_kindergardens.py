from drf_spectacular.utils import OpenApiExample

ErrorPetKindergardenNotFoundSchema = OpenApiExample(
    name="404(pet_kindergarden_not_found)",
    summary="[Not Found]: Pet Kindergarden Not Found",
    description="""
    해당 반려동물 유치원을 찾을 수 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 404,
        "code": "not_found_pet_kindergarden",
        "message": "Pet Kindergarden does not exist.",
        "data": {},
    },
    status_codes=["404"],
    response_only=True,
)