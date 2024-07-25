from passlib.context import CryptContext

# CryptContext 객체를 생성하고 bcrypt 해시 알고리즘을 설정합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """비밀번호를 해싱합니다."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """해시된 비밀번호를 검증합니다."""
    return pwd_context.verify(plain_password, hashed_password)
