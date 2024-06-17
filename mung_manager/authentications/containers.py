from dependency_injector import containers, providers

from mung_manager.authentications.selectors.users import UserSelector
from mung_manager.authentications.services.auth import AuthService
from mung_manager.authentications.services.kakao_oauth import KakaoLoginFlowService
from mung_manager.authentications.services.users import UserService


class AuthenticationContainer(containers.DeclarativeContainer):
    """이 클래스는 DI(Dependency Injection) 인증 컨테이너 입니다.

    Attributes:
        auth_service: 인증 서비스
        kakao_login_flow_service: 카카오 로그인 플로우 서비스
    """

    auth_service = providers.Factory(AuthService)
    kakao_login_flow_service = providers.Factory(KakaoLoginFlowService)

    user_selector = providers.Factory(UserSelector)
    user_service = providers.Factory(
        UserService,
        user_selector=user_selector,
    )
