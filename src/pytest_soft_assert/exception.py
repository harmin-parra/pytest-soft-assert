class SoftAssertionError(Exception): ...


class _ExcInfo:
    def __init__(self):
        self.type = None
        self.value = None
        self.traceback = None

    def update(self, e: Exception):
        self.type = type(e)
        self.value = e
        self.traceback = e.__traceback__
