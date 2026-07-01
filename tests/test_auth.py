import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.api.dependencies import (
    verify_collector_token,
    verify_teacher_token,
    verify_teacher_or_collector_token,
    get_collector_token,
    get_teacher_token
)

def test_verify_collector_token_valid():
    token = get_collector_token()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    assert verify_collector_token(credentials) == token

def test_verify_collector_token_invalid():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
    with pytest.raises(HTTPException) as exc_info:
        verify_collector_token(credentials)
    assert exc_info.value.status_code == 403

def test_verify_teacher_token_valid():
    token = get_teacher_token()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    assert verify_teacher_token(credentials) == token

def test_verify_teacher_token_invalid():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
    with pytest.raises(HTTPException) as exc_info:
        verify_teacher_token(credentials)
    assert exc_info.value.status_code == 403

def test_verify_teacher_or_collector_token():
    teacher_token = get_teacher_token()
    collector_token = get_collector_token()
    
    cred_t = HTTPAuthorizationCredentials(scheme="Bearer", credentials=teacher_token)
    assert verify_teacher_or_collector_token(cred_t) == "teacher"
    
    cred_c = HTTPAuthorizationCredentials(scheme="Bearer", credentials=collector_token)
    assert verify_teacher_or_collector_token(cred_c) == "collector"
    
    cred_inv = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")
    with pytest.raises(HTTPException) as exc_info:
        verify_teacher_or_collector_token(cred_inv)
    assert exc_info.value.status_code == 403
