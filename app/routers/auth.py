from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    ProfileUpdate,
    ProfileUpdateResponse,
    Token,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)


@router.post("/login/json", response_model=Token)
def login_json(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        # El registro público nunca asigna roles: se ignora el "role" enviado por el cliente.
        # Solo un administrador puede asignar roles mediante POST /api/users.
        role="user",
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=ProfileUpdateResponse)
def update_me(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    changes = data.model_dump(exclude_unset=True)

    if "username" in changes and db.query(User).filter(
        User.username == changes["username"], User.id != current_user.id
    ).first():
        raise HTTPException(status_code=409, detail="El nombre de usuario ya existe")
    if "email" in changes and db.query(User).filter(
        User.email == changes["email"], User.id != current_user.id
    ).first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    for field, value in changes.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    # El token guarda el username en "sub": se emite uno nuevo por si cambió.
    access_token = create_access_token(data={"sub": current_user.username})
    return ProfileUpdateResponse(user=current_user, access_token=access_token)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
    if verify_password(data.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="La nueva contraseña debe ser distinta de la actual")

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
