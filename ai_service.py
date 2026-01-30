from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from config import GIGACHAT_TOKEN

# Промпт для нейросети
SYSTEM_PROMPT = (
    "Ты — профессиональный бизнес-консультант Сбера. "
    "Твоя цель — помогать начинающим предпринимателям открывать бизнес в РФ. "
    "Отвечай кратко, вежливо, используй структуру и списки. "
    "Если вопрос не касается бизнеса, вежливо напомни, что ты бизнес-ассистент."
)


async def ask_gigachat(user_question: str):
    """
    Отправляет запрос в GigaChat и возвращает текст ответа.
    """
    if not GIGACHAT_TOKEN:
        return "Ошибка: Токен GigaChat не найден в файле .env"

    try:
        # Контекстный менеджер
        async with GigaChat(
                credentials=GIGACHAT_TOKEN,
                scope="GIGACHAT_API_PERS",
                verify_ssl_certs=False
        ) as giga:
            # Структура сообщения
            messages = [
                Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                Messages(role=MessagesRole.USER, content=user_question)
            ]
            response = giga.chat(payload=Chat(messages=messages))
            return response.choices[0].message.content

    except Exception as e:
        print(f"Ошибка при запросе к GigaChat: {e}")
        return f"Не удалось связаться с нейросетью. Попробуйте еще раз."