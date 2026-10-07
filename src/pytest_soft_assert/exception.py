class SoftAssertionError(Exception):

    def __str__(self) -> str:
        return "\n\n".join(getattr(self, "__notes__", []))
