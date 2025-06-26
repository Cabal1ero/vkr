from ninja import Router, Schema
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from typing import Optional
from users.models import User

router = Router()

# Schemas
class RegisterSchema(Schema):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class LoginSchema(Schema):
    email: str
    password: str

class UserSchema(Schema):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Endpoints
@router.post("/register", response={201: UserSchema, 400: dict})
def register(request, payload: RegisterSchema):
    """
    Register a new user.
    """
    try:
        user = User.objects.create_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name
        )
        return 201, user
    except Exception as e:
        return 400, {"message": str(e)}

@router.post("/login", response={200: UserSchema, 400: dict})
def user_login(request, payload: LoginSchema):
    """
    Login a user.
    """
    user = authenticate(request, email=payload.email, password=payload.password)
    if user is not None:
        login(request, user)
        return 200, user
    return 400, {"message": "Invalid credentials"}

@router.post("/logout")
def user_logout(request):
    """
    Logout a user.
    """
    logout(request)
    return {"message": "Successfully logged out"}

@router.get("/user", response=UserSchema)
def get_user(request):
    """
    Get the current user.
    """
    if not request.user.is_authenticated:
        return 401, {"message": "Unauthorized"}
    return request.user 