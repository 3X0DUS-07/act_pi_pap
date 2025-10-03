from fastapi import HTTPException
from starlette import status


class RecipeAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(RecipeAPIException):
    def __init__(self, resource: str, identifier: str = None):
        detail = f"{resource} not found"
        if identifier:
            detail += f" with identifier: {identifier}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsError(RecipeAPIException):
    def __init__(self, resource: str, field: str = None, value: str = None):
        detail = f"{resource} already exists"
        if field and value:
            detail += f" with {field}: {value}"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationError(RecipeAPIException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)