import os
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    ConversationState,
    MemoryStorage,
)
from botbuilder.schema import Activity
from main_bot import AtendimentoBot

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

memory = MemoryStorage()
conversation_state = ConversationState(memory)
bot = AtendimentoBot(conversation_state)
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

async def messages(req):
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    async def aux_func(turn_context):
        await bot.on_turn(turn_context)

    response = await adapter.process_activity(activity, auth_header, aux_func)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=201)

app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    web.run_app(app, host="localhost", port=3978)