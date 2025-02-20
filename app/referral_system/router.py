from typing import List
from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User

router = APIRouter()
