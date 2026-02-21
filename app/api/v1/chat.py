from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.session import Session 
from app.models.message import Message 
from app.schemas.message import MessageCreate, MessageResponse, ChatHistoryResponse
from app.services.gemini import generate_chat_response

# Task 6.1
router = APIRouter(prefix="/sessions/{session_id}/chat", tags=["Chat"])

async def verify_session(session_id: UUID, db: AsyncSession):
    stmt = select(Session).where(Session.id == session_id)
    session = (await db.execute(stmt)).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")
    return session

# Task 5.2 - 5.8
@router.post("", response_model=MessageResponse)
async def send_message(session_id: UUID, payload: MessageCreate, db: AsyncSession = Depends(get_db)):
    await verify_session(session_id, db)
    
    # Ambil history
    stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    db_history = (await db.execute(stmt)).scalars().all()
    
    # Simpan pesan user
    user_msg = Message(session_id=session_id, role="user", content=payload.message)
    db.add(user_msg)
    await db.flush() # Flush agar id di-generate tanpa memutus transaksi
    
    # Dapatkan balasan AI
    ai_reply_text = await generate_chat_response(payload.message, db_history)
    
    # Simpan balasan AI
    ai_msg = Message(session_id=session_id, role="model", content=ai_reply_text)
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)
    
    return ai_msg

# Task 5.9 - 5.12
@router.get("", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: UUID, db: AsyncSession = Depends(get_db)):
    await verify_session(session_id, db)
    stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    messages = (await db.execute(stmt)).scalars().all()
    return ChatHistoryResponse(session_id=session_id, messages=messages)