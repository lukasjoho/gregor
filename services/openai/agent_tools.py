from typing import Literal, Union
from agents import function_tool
from agents.tool import FileSearchTool, WebSearchTool
from services.database.database import get_data
from services.database.types import Product, Question, Store, Tip

from services.whatsapp.messages.reaction_message import send_reaction_message
from services.whatsapp.messages.text_message import send_text_message

import os
from dotenv import load_dotenv

from services.whatsapp.messages.typing_message import send_typing_indicator
from services.whatsapp.types import ReactionMessageData, TextMessageData, TypingMessageData

load_dotenv()

def create_tools(phone_number: str, message_id: str):
    @function_tool
    def get_belcando_data(data_type: Literal["products", "stores", "tips"]) -> Union[list[Product], list[Store], list[Tip]]:
        """Get Belcando data from the database.
        
        Args:
            data_type: Type of data to retrieve - "products", "stores", "tips"
        """
        return get_data(f"{data_type}.json")

    @function_tool
    def send_status_text(text: str):
        """Send a short intermediate status update line to the user while you are working on longer research tasks.
        Args:
            text: The message that is sent to the user's message.
        """
        print(f"Sending status text: {text}")
        data = TextMessageData(text=text)
        send_text_message(phone_number, data)
        return "TOOL RESPONSE: Status sent"

    @function_tool
    def send_reaction(emoji: str):
        """Send a emoji reaction to the user's message.
        Args:
            emoji: Single emoji, that is sent to the user's message (e.g. 🐕, 👍, 🤔, ❤️, 😊, 🎉, etc.)
        """
        reaction_data = ReactionMessageData(message_id=message_id, emoji=emoji)
        send_reaction_message(phone_number, reaction_data)
        return "TOOL RESPONSE: Emoji sent"

    @function_tool
    def send_typing(message_id: str):
        """Send a typing indicator to the user's message. (Only use this if you are working on a longer task. You can do this greatly after retrievla operations and before sending the final result to let the user know you are about to send the final result.)
        Args:
            message_id: The ID of the message to send the typing indicator for
        """
        typing_data = TypingMessageData(message_id=message_id)
        send_typing_indicator(typing_data)
        return "TOOL RESPONSE: Typing indicator sent"


    knowledge_tools = [get_belcando_data]
    communication_tools = [send_reaction, send_status_text]
    tools = knowledge_tools + communication_tools
    
    # Add FileSearchTool if vector store is available
    vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")
    if vector_store_id:
        file_search_tool = FileSearchTool(vector_store_ids=[vector_store_id])
        tools.append(file_search_tool)

    website_search_tool = WebSearchTool()
    tools.append(website_search_tool)
    
    return tools