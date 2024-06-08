class SYSTEM_CODE:
    # Default code
    SUCCESS = ("request_success", "Request was successful.")
    BAD_REQUEST = ("bad_request", "Bad request.")
    INVALID_PARAMETER_FORMAT = (
        "invalid_parameter_format",
        "The parameter format is incorrect.",
    )
    VALIDATION_FAILED = ("validation_failed", "Validation failed.")
    ALREADY_EXISTS = ("already_exists", "This object already exists.")
    INVALID_TOKEN = ("token_not_valid", "Token is invalid or expired.")
    AUTHENTICATION_FAILED = (
        "authentication_failed",
        "Incorrect authentication credentials.",
    )
    PERMISSION_DENIED = (
        "permission_denied",
        "You do not have permission to perform this action.",
    )
    NOT_FOUND = ("not_found", "Not found.")
    UNKNOWN_SERVER_ERROR = (
        "unknown_server_error",
        "An unknown server error occurred.",
    )
    NOT_IMPLEMENTED = (
        "not_implemented",
        "This feature is not implemented yet.",
    )

    # Common code
    INVALID_PHONE_NUMBER = (
        "validation_failed",
        "Enter a valid phone number (e.g. 010-0000-0000)",
    )

    # Auth code
    NOT_FOUND_AUTH_USER = ("authentication_failed", "User not found")
    INACTIVE_AUTH_USER = ("authentication_failed", "User is inactive")
    DELETED_AUTH_USER = ("authentication_failed", "User is deleted")
    REVOKE_TOKEN_AUTH_USER = (
        "authentication_failed",
        "The user's password has been changed.",
    )
    INVALID_TOKEN_AUTH_USER_IDENTIFICATION = (
        "token_not_valid",
        "Token contained no recognizable user identification",
    )

    # Oauth code
    AUTHENTICATION_FAILED_KAKAO_ADDRESS = (
        "authentication_failed",
        "Failed to get coordinates from Kakao.",
    )

    # User code
    NOT_AUTHENTICATED_KAKAO_PHONE_NUMBER = (
        "authentication_failed",
        "Kakao phone number is not authenticated.",
    )
    ALREADY_EXISTS_EMAIL = ("already_exists", "Email already exists.")

    # Pet kindergarden code
    NOT_FOUND_PET_KINDERGARDEN = (
        "not_found_pet_kindergarden",
        "Pet kindergarden does not exist.",
    )
    ALREADY_EXISTS_USER_PET_KINDERGARDEN = (
        "already_exists_user_pet_kindergarden",
        "User already has a pet kindergarden.",
    )

    # Reservation code
    NOT_FOUND_DAY_OFF = ("not_found_day_off", "Day off does not exist.")
    ALREADY_EXISTS_DAY_OFF = ("already_exists_day_off", "Day off already exists.")
    NOT_FOUND_RESERVATION = ("not_found_reservation", "Reservation does not exist.")
    ALREADY_EXISTS_RESERVATION_CUSTOMER_PET = (
        "already_exists_reservation_customer_pet",
        "Reservation already exists for customer pet.",
    )
    INVALID_RESERVED_AT = (
        "validation_failed",
        "The reservation can only be scheduled for dates after the current time.",
    )
    INVALID_END_AT = ("validation_failed", "The reservation end time must be later than the start time.")

    # Ticket code
    NOT_FOUND_TICKET = ("not_found_ticket", "Ticket does not exist.")

    # File code
    MAX_FILE_SIZE = ("validation_failed", "File is too large. Max File Size")
    INVALID_FILE_TYPE = ("validation_failed", "Invalid file type")
    DUPLICATE_PHONE_NUMBER_CSV_FILE = (
        "validation_failed",
        "Csv file phone number is duplicated.",
    )

    # Customer code
    UNIQUE_PET_NAME = ("unique_pet_name", "Customer pet names must be unique.")
    NOT_FOUND_CUSTOMER = ("not_found_customer", "Customer does not exist.")
    NOT_FOUND_CUSTOMER_PET = (
        "not_found_customer_pet",
        "Customer pet does not exist.",
    )
    NOT_FOUND_CUSTOMER_TICKET = (
        "not_found_customer_ticket",
        "Customer ticket does not exist.",
    )
    ALREADY_EXISTS_CUSTOMER = (
        "already_exists_customer",
        "Customer already exists.",
    )
    ALREADY_EXISTS_CUSTOMER_PET = (
        "already_exists_customer_pet",
        "Customer pet already exists.",
    )
    NO_CUSTOMER_TICKET_COUNT = (
        "no_customer_ticket_count",
        "There are no remaining ticket counts.",
    )
    CONFILCT_CUSTOMER_TICKET = (
        "conflict_customer_ticket",
        "A conflict occurred while using the ticket. Please try again.",
    )

    @classmethod
    def code(cls, code: str) -> str:
        return getattr(cls, code)[0]

    @classmethod
    def message(cls, code: str) -> str:
        return getattr(cls, code)[1]
