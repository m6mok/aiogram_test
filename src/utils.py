ERROR_MESSAGE = 'Произошла ошибка, попробуйте позже'


class Singleton:
    obj = None

    def __new__(cls, *args, **kwargs):
        if cls.obj is None:
            cls.obj = object.__new__(cls)
        return cls.obj
