import aiohttp
from fuzzywuzzy import fuzz
from botbuilder.core import ActivityHandler, TurnContext, ConversationState

# Palavras-chave principais e respostas
INTENT_KEYWORDS = {
    "calendario": "O calendário está disponível em: www.exemplo.edu/calendario",
    "boleto": "Acesse o portal do aluno e clique em 'Financeiro'.",
    "horario": "De segunda a sexta, das 19h às 22h.",
    "secretaria": "secretaria@exemplo.edu",
    "matricula": "Vamos iniciar sua matrícula! Qual seu nome completo?"
}

class AtendimentoBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState):
        self.conversation_state = conversation_state
        self.user_state_accessor = self.conversation_state.create_property("matricula_state")

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Bem-vindo! O que deseja hoje?")

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.lower().strip()
        state = await self.user_state_accessor.get(turn_context, None)
        if state is None:
            state = {}

        # Processo de matrícula dinâmico
        if state.get("matricula") == "nome":
            state["nome"] = turn_context.activity.text
            state["matricula"] = "email"
            await turn_context.send_activity("Qual seu e-mail?")
            await self.user_state_accessor.set(turn_context, state)
            await self.conversation_state.save_changes(turn_context)
            return
        elif state.get("matricula") == "email":
            state["email"] = turn_context.activity.text
            state["matricula"] = "curso"
            await turn_context.send_activity("Qual curso deseja se matricular?")
            await self.user_state_accessor.set(turn_context, state)
            await self.conversation_state.save_changes(turn_context)
            return
        elif state.get("matricula") == "curso":
            state["curso"] = turn_context.activity.text
            payload = {
                "nome": state["nome"],
                "email": state["email"],
                "curso": state["curso"]
            }
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post("https://webappchatbot-ababd4czbpeshcde.westus-01.azurewebsites.net/api/matriculas", json=payload) as resp:
                        resposta_backend = await resp.text()
                        if resp.status == 200 or resp.status == 201:
                            await turn_context.send_activity(f"{resposta_backend} Sua matrícula foi registrada!")
                        else:
                            await turn_context.send_activity(f"Erro ao registrar matrícula: {resposta_backend}")
                except Exception as e:
                    await turn_context.send_activity(f"Erro ao registrar matrícula no backend: {str(e)}")
            state.clear()
            await self.user_state_accessor.set(turn_context, state)
            await self.conversation_state.save_changes(turn_context)
            return

        # Fuzzy matching ultra flexível com prefixo e abreviação
        melhor_intencao = None
        melhor_score = 0
        for palavra, resposta in INTENT_KEYWORDS.items():
            score = fuzz.token_set_ratio(palavra, text)
            # Aceita se a palavra-chave ou seu prefixo está na frase
            if palavra in text or palavra[:5] in text:
                score = 100
            if score > melhor_score:
                melhor_score = score
                melhor_intencao = palavra

        if melhor_score > 50:
            resposta = INTENT_KEYWORDS[melhor_intencao]
            if melhor_intencao == "matricula":
                state["matricula"] = "nome"
                await self.user_state_accessor.set(turn_context, state)
                await self.conversation_state.save_changes(turn_context)
            await turn_context.send_activity(resposta)
            return

        await turn_context.send_activity("Desculpe, não entendi. Pode reformular?")