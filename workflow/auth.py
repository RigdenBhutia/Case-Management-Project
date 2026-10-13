import os
from typing import Optional

from fastapi import Depends, Header, HTTPException

API_KEYS = {
    os.getenv("REQUESTER_API_KEY", "requester-dev-key"): {"user": "alice", "role": "requester"},
    os.getenv("APPROVER_API_KEY", "approver-dev-key"): {"user": "bob", "role": "approver"},
}


def get_user(x_api_key: Optional[str] = Header(default=None)):
    user = API_KEYS.get(x_api_key)
    if user is None:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
    return user


def require_role(*roles: str):
    def checker(user: dict = Depends(get_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Your role is not allowed to do this")
        return user
    return checker