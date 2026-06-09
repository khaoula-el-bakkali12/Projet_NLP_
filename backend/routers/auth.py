import os
import json
import sqlite3
import hashlib
import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["auth"])

_USERS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "users.json")
_DB_PATH    = os.path.join(os.path.dirname(__file__), "..", "..", "data", "oncologia.db")


def _load_users() -> dict:
    try:
        with open(_USERS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_users(users: dict):
    os.makedirs(os.path.dirname(_USERS_PATH), exist_ok=True)
    with open(_USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    username: str
    token: str


@router.post("/auth/login", response_model=AuthResponse)
def login(req: AuthRequest):
    users = _load_users()
    if req.username not in users:
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect.")
    if users[req.username]["password"] != _hash(req.password):
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect.")
    token = secrets.token_hex(32)
    return AuthResponse(username=req.username, token=token)


@router.post("/auth/register", response_model=AuthResponse)
def register(req: AuthRequest):
    if len(req.username) < 3:
        raise HTTPException(status_code=400, detail="L'identifiant doit contenir au moins 3 caractères.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères.")
    users = _load_users()
    if req.username in users:
        raise HTTPException(status_code=409, detail="Cet identifiant est déjà utilisé.")
    users[req.username] = {"password": _hash(req.password)}
    _save_users(users)
    token = secrets.token_hex(32)
    return AuthResponse(username=req.username, token=token)


class ProfileUpdateRequest(BaseModel):
    username: str
    current_password: str
    new_username: Optional[str] = None
    new_password: Optional[str] = None


def _rename_history_user(old: str, new: str):
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            conn.execute("UPDATE history SET username = ? WHERE username = ?", (new, old))
            conn.commit()
    except Exception as e:
        print(f"[auth] History rename failed: {e}")


@router.put("/auth/profile")
def update_profile(req: ProfileUpdateRequest):
    users = _load_users()

    if req.username not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    if users[req.username]["password"] != _hash(req.current_password):
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect.")

    # Determine what actually changes
    changing_username = req.new_username and req.new_username.strip() and req.new_username != req.username
    changing_password = bool(req.new_password)

    if not changing_username and not changing_password:
        raise HTTPException(status_code=400, detail="Aucune modification détectée.")

    final_username = req.username

    if changing_username:
        new_name = req.new_username.strip()
        if len(new_name) < 3:
            raise HTTPException(status_code=400, detail="L'identifiant doit contenir au moins 3 caractères.")
        if new_name in users:
            raise HTTPException(status_code=409, detail="Cet identifiant est déjà utilisé.")
        users[new_name] = users.pop(req.username)
        final_username = new_name
        _rename_history_user(req.username, new_name)

    if changing_password:
        if len(req.new_password) < 6:
            raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit contenir au moins 6 caractères.")
        users[final_username]["password"] = _hash(req.new_password)

    _save_users(users)
    return {"username": final_username, "message": "Profil mis à jour avec succès."}
