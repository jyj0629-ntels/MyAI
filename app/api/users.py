from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

from app.schemas.user import UserCreate
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get(
    "/{email}",
    response_model=UserResponse
)
def get_user(
    email: str,
    db: Session = Depends(get_db)
):

    service = UserService(
        UserRepository(db)
    )

    user = service.get_user(email)

    if not user:
        return {
            "id": 0,
            "email": "",
            "name": "not found"
        }

    return user


@router.post(
    "/",
    response_model=UserResponse
)
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db)
):

    service = UserService(
        UserRepository(db)
    )

    return service.create_user(
        email=request.email,
        name=request.name
    )
