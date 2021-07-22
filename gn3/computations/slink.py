class LengthError(BaseException):
    pass

class MirrorError(BaseException):
    pass

def raise_valueerror_if_data_is_not_lists_or_tuples(lists):
    """Check that `lists` is a list of lists: If not, raise an exception."""
    def is_list_or_tuple(item):
        return type(item) == type([]) or type(item) == type(tuple)

    if (not is_list_or_tuple(lists)) or (not all(map(is_list_or_tuple, lists))):
        raise ValueError("Expected list or tuple")

def nearest(lists, i, j):
    raise_valueerror_if_data_is_not_lists_or_tuples(lists)
    return None
