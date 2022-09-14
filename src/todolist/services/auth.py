from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .. import tables
from ..database import get_session
from ..settings import settings
from ..models.auth import User, UserCreate, Token

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign-in')


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return AuthService.validate_token(token)


class AuthService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password):
        return pwd_context.hash(password)


    @classmethod
    def create_token(
            cls, user: tables.User,
            expires_delta: timedelta | None = None
    ) -> Token:
        user_data = User.from_orm(user)

        now = datetime.utcnow()
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=15)
        payload = {
            'exp': expire,
            'sub': str(user_data.id),
            'user': user_data.dict(),
        }
        token = jwt.encode(
            payload,
            key=settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        return Token(access_token=token)

    @classmethod
    def validate_token(cls, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(
                token,
                key=settings.jwt_secret,
                algorithms=[settings.jwt_algorithm,]
            )
        except JWTError:
            raise credentials_exception from None
        user_data = payload.get('user')
        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise credentials_exception from None
        return user

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def register_new_user(self, user_data: UserCreate) -> Token:
        user_in_db = (
            self.session
            .query(tables.User)
            .filter_by(username=user_data.username)
            .first()
        )
        if user_in_db:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Username already exists')
        user_in_db = (
            self.session
            .query(tables.User)
            .filter_by(email=user_data.email)
            .first()
        )
        if user_in_db:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User email already exists')

        user = tables.User(
            username=user_data.username,
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=self.get_password_hash(user_data.password)
        )
        self.session.add(user)
        self.session.commit()

        return self.create_token(user=user)

    def authenticate_user(self, username: str, password: str) -> Token:
        auth_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.username == username)
            .first()
        )
        if not user:
            raise auth_exception

        if not self.verify_password(password, user.hashed_password):
            raise  auth_exception

        return self.create_token(user)

