from mung_manager.errors.exceptions import AlreadyExistsException, NotFoundException


def get_object_or_not_found(objects, msg, code):
    if objects is None:
        if msg:
            raise NotFoundException(msg, code)
    return objects


def check_object_or_not_found(is_exists, msg, code):
    if is_exists is False:
        if msg:
            raise NotFoundException(msg, code)
    return is_exists


def check_object_or_already_exist(is_exists, msg, code):
    if is_exists is True:
        if msg:
            raise AlreadyExistsException(msg, code)
    return is_exists
