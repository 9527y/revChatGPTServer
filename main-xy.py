from subprocess import Popen
from typing import Optional
# from revChatGPT.revChatGPT import Chatbot
from revChatGPT.V1 import Chatbot
from fastapi import FastAPI, Response, status
import json
import uuid
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel


class Item(BaseModel):
    prompt: str
    conversation_id: Optional[str]
    parent_id: Optional[str]


with open("config.json", "r") as f:
    config = json.load(f)
chatbot = Chatbot(config)


@app.post("/")
async def read_root(body: Item, response: Response):
    data = {
        "action": "next",
        "messages": [
            {"id": str(uuid.uuid4()),
             "role": "user",
             "content": {"content_type": "text", "parts": [body.prompt]}
             }],
        "conversation_id": body.conversation_id if body.conversation_id else None,
        "parent_message_id": body.parent_id if body.parent_id else str(uuid.uuid4()),
        "model": "text-davinci-002-render"
    }
    logger.info(data)
    try:
        result = chatbot.ask(body.prompt, parent_id=body.parent_id, conversation_id=body.conversation_id, timeout=10)
        if result:
            return {"response": result}
        else:
            raise Exception("No response")
    except Exception as e:
        chatbot.reset_chat()
        try:
            result = chatbot.ask(body.prompt, parent_id=body.parent_id, conversation_id=body.conversation_id,
                                 timeout=10)
            if result:
                return {"response": result}
            else:
                raise Exception("No response")
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise e
            return {"response": "Error"}


if __name__ == '__main__':
    Popen(['python', '-m', 'https_redirect'])  # Add this
    uvicorn.run(
        'main:app',
        port=8878,
        host='0.0.0.0',
        reload=True,
        reload_dirs=['html_files'],
        # ssl_keyfile='/etc/letsencrypt/live/my_domain/privkey.pem',
        # ssl_certfile='/etc/letsencrypt/live/my_domain/fullchain.pem'
    )
