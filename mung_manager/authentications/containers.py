from dependency_injector import containers, providers

from mung_manager.authentications.selectors.users import UserSelector
from mung_manager.authentications.services.auth import AuthService
from mung_manager.authentications.services.kakao_oauth import KakaoLoginFlowService
from mung_manager.authentications.services.users import UserService
from mung_manager.customers.selectors.customers import CustomerSelector


class AuthenticationContainer(containers.DeclarativeContainer):
    """
    이 클래스는 DI(Dependency Injection) 인증 컨테이너 입니다.

    Attributes:
        customer_selector: 고객 셀렉터
        auth_service: 인증 서비스
        kakao_login_flow_service: 카카오 로그인 플로우 서비스
        user_selector: 유저 셀렉터
        user_service: 유저 서비스
    """

    customer_selector = providers.Factory(CustomerSelector)
    auth_service = providers.Factory(AuthService, customer_selector=customer_selector)
    kakao_login_flow_service = providers.Factory(KakaoLoginFlowService)
    user_selector = providers.Factory(UserSelector)
    user_service = providers.Factory(
        UserService,
        user_selector=user_selector,
    )
