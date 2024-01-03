import logging
from typing import AsyncIterable

from langchain.schema.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks import AsyncIteratorCallbackHandler
from ..db.sql_manager import SqlManager

from config.config import settings

logger = logging.getLogger(__name__)


class GeminiLLMManager:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.sql_manager = SqlManager()
        self.conversation_chain = None
        self.callback = AsyncIteratorCallbackHandler()

    def get_gemini_model(self, image: bool = False):
        if image:
            model = ChatGoogleGenerativeAI(
                google_api_key=settings.GEMINI_API_KEY,
                stream=True,
                model="gemini-pro-vision",
                convert_system_message_to_human=True,
                callbacks=[self.callback],
            )
        else:
            model = ChatGoogleGenerativeAI(
                google_api_key=settings.GEMINI_API_KEY,
                stream=True,
                model="gemini-pro",
                convert_system_message_to_human=True,
                callbacks=[self.callback],
            )

        return model

    async def generate_async_response(
        self,
        message: str,
        conversation_id: str,
        image: bool = False,
        image_url: str = None,
    ) -> AsyncIterable[str]:
        model = self.get_gemini_model(image)
        memory = self.sql_manager.create_or_get_memory(conversation_id=conversation_id)
        chat_memory = memory.load_memory_variables({})
        history = chat_memory["chat_history"]

        if not history:
            if image_url and image:
                message_list = [
                    SystemMessage(content=settings.SYSTEM_INSTRUCTION),
                    HumanMessage(
                        content=[
                            {
                                "type": "text",
                                "text": message,
                            },  # You can optionally provide text parts
                            {"type": "image_url", "image_url": image_url},
                        ]
                    ),
                ]
            else:
                message_list = [
                    SystemMessage(content=settings.SYSTEM_INSTRUCTION),
                    HumanMessage(content=message),
                ]

        else:
            if image_url and image:
                message_list = [SystemMessage(content=settings.SYSTEM_INSTRUCTION)] + [
                    HumanMessage(
                        content=[
                            {
                                "type": "text",
                                "text": message,
                            },  # You can optionally provide text parts
                            {"type": "image_url", "image_url": image_url},
                        ]
                    )
                ]
            else:
                message_list = (
                    [SystemMessage(content=settings.SYSTEM_INSTRUCTION)]
                    + history
                    + [HumanMessage(content=message)]
                )
        response = ""

        async for token in model.astream(input=message_list):
            response += f"{repr(token.content)}"
            yield f"{repr(token.content)}".encode("utf-8", errors="replace")

        await self.sql_manager.add_conversation_to_memory(
            conversation_id, message, response
        )
