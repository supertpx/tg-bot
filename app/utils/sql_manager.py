import logging
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from datetime import datetime
from typing import Any

from langchain.memory.chat_message_histories.sql import BaseMessageConverter
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.orm import declarative_base
from config.config import settings


logger = logging.getLogger(__name__)


class SqlManager:
    def __init__(self):
        self.db_url = settings.DB_URL

    def create_or_get_memory(self, conversation_id):
        message_history = SQLChatMessageHistory(
            connection_string=self.db_url,
            session_id=conversation_id,
            custom_message_converter=CustomMessageConverter(author_email="tpx@x.com"),
        )
        return ConversationBufferWindowMemory(
            memory_key="chat_history",
            chat_memory=message_history,
            return_messages=True,
            max_token_limit=4000,
        )

    async def add_conversation_to_memory(
        self, conversation_id, user_message, ai_message
    ):
        history = self.create_or_get_memory(conversation_id)
        history.save_context({"input": user_message}, {"output": ai_message})


Base = declarative_base()


class CustomMessage(Base):
    __tablename__ = "message_store"

    id = Column(Integer, primary_key=True)
    session_id = Column(Text)
    type = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime)
    author_email = Column(Text)


class CustomMessageConverter(BaseMessageConverter):
    def __init__(self, author_email: str):
        self.author_email = author_email

    def from_sql_model(self, sql_message: Any) -> BaseMessage:
        if sql_message.type == "human":
            return HumanMessage(
                content=sql_message.content,
            )
        elif sql_message.type == "ai":
            return AIMessage(
                content=sql_message.content,
            )
        elif sql_message.type == "system":
            return SystemMessage(
                content=sql_message.content,
            )
        else:
            raise ValueError(f"Unknown message type: {sql_message.type}")

    def to_sql_model(self, message: BaseMessage, session_id: str) -> Any:
        now = datetime.now()
        return CustomMessage(
            session_id=session_id,
            type=message.type,
            content=message.content,
            created_at=now,
            author_email=self.author_email,
        )

    def get_sql_model_class(self) -> Any:
        return CustomMessage
