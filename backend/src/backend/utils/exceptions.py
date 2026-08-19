from fastapi import HTTPException


def _raise_http(code: int, msg: str) -> None:
    raise HTTPException(status_code=code, detail=msg)

class DBConnectionError(Exception):
    def __init__(self):
        super().__init__()
