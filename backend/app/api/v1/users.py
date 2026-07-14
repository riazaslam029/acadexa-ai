from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    DashboardResponse,
    UserPasswordChange,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    change_user_password,
    delete_user_account,
    get_user_dashboard,
    update_user_profile,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_profile(db, current_user, payload)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    payload: UserPasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_user_password(db, current_user, payload)


@router.delete(
    "/me",
)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_user_account(db, current_user)
    return {"message": "Account deleted successfully."}


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_dashboard(db, current_user)