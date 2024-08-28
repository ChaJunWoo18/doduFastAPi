# import smtplib, ssl

# def send_verification_email(to_email: str, code: str):
#     from_email = "lsbfodng@gmail.com"
#     from_password = "dnjsendenql!123"

#     msg = MIMEText(f"이메일 인증코드는 {code} 입니다.")
#     msg['Subject'] = '[DOBU]이메일 인증 코드'
#     msg['From'] = from_email
#     msg['To'] = to_email

#     try:
#         server = smtplib.SMTP_SSL('smtp.gmail.com', 587) 
#         server.login(from_email, from_password)
#         server.sendmail(from_email, to_email, msg.as_string())
#         server.quit()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Failed to send verification email.")
from pydantic import EmailStr, BaseModel
from typing import List
from fastapi import BackgroundTasks, HTTPException, Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from starlette.responses import JSONResponse
from fastapi import APIRouter

class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = "lsbfodng@gmail.com",
    MAIL_PASSWORD = "nijh iupd rqjk nrmh",
    MAIL_FROM = "lsbfodng@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="[DODU]",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# 인증번호 저장소 (예시로 메모리에서 관리)
verification_codes = {}

class EmailVerificationRequest(BaseModel):
    email: EmailStr

router = APIRouter()

import random
import string
from redisConfig import rd


def generate_verification_code(length=6):
    # 대문자와 숫자로 이루어진 문자 집합
    characters = string.ascii_uppercase + string.digits
    
    verification_code = ''.join(random.choice(characters) for _ in range(length))
    return verification_code

# 인증번호 생성 및 저장
def store_verification_code(email):
    verification_code = generate_verification_code()
    
    # 인증번호와 생성 시간 저장
    rd.set(f"{email}_verification_code", verification_code, ex=180)  # 180초 = 3분 TTL 설정
    
    return verification_code

@router.post("/send/verify/email/background")
async def send_in_background(background_tasks: BackgroundTasks,
                            email: EmailSchema) -> JSONResponse:
    # 인증번호 생성 및 redis저장
    request_email = email.email[0]
    verification_code = store_verification_code(request_email)
    
    # 이메일 내용
    html = f"""<p>인증코드는</p>
    <p style='font-size: 24px;'><b>{verification_code}</b></p>"""

    message = MessageSchema(
        subject="[DODU]인증번호 발송",
        recipients=email.dict().get("email"),
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})

def is_code_valid(email, input_code):
    # Redis에서 인증번호 가져오기
    stored_code = rd.get(f"{email}_verification_code")
    #print(stored_code)
    # 인증번호 존재 여부와 일치 여부 확인
    if stored_code is None:
        return False
    
    return input_code == stored_code.decode('utf-8')

class VerifyRequest(BaseModel):
    email: str
    input_code: str

@router.post("/verify/email_code")
def verifyCode(request: VerifyRequest):
    is_ok = is_code_valid(request.email, request.input_code)
    if is_ok:
        return {"message": "Verification successful"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
