from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from ai_service import ask_gigachat

from states import RegistrationFlow
from keyboards import kb_main_menu, kb_ai_chat, kb_back_to_menu

router_menu = Router()


# Блок: Глобальная навигация

# Обработка кнопки "В главное меню" или /menu на любом этапе
@router_menu.message(StateFilter("*"), F.text.in_({"В главное меню", "/menu"}))
@router_menu.message(StateFilter("*"), Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Привет! Я бизнес-ассистент.</b>\n\n"
        "В этом чат-боте вы сможете составить собственный план по открытию бизнеса "
        "используя пошаговый опросник по кнопке <b>\"Составить бизнес-план\"</b>, "
        "либо получить ответ на конкретный вопрос во вкладке <b>\"Спросить у GigaChat\"</b>\n\n"
        "Что выберете?",
        parse_mode="HTML", reply_markup=kb_main_menu
    )


# Главное меню

# 1. Сценарий нажатия: "Составить бизнес-план"
@router_menu.message(F.text == "Составить бизнес-план")
async def start_survey(message: Message, state: FSMContext):
    await message.answer(
        "В режиме опроса вы получите готовый бизнес-план, основанный на ваших выборах. "
        "Также на каждом шаге имеется возможность получить справочный материал по теме вопроса. "
        "В конце будут представлены ссылки для более подробной информации.\n\n"
        
        "Начнем! Как будет называться ваш бизнес?\n"
        "Напишите название в чат.",
        reply_markup=kb_back_to_menu
    )
    await state.set_state(RegistrationFlow.waiting_for_business_name)


# 2. Сценарий нажатия: "Спросить у GigaChat"
@router_menu.message(F.text == "Спросить у GigaChat")
async def start_ai_chat(message: Message, state: FSMContext):
    await message.answer(
        "Чат с AI активирован.\n\n"
        
        "Задайте любой вопрос. Нажмите кнопку внизу, чтобы выйти.",
        reply_markup=kb_ai_chat
    )
    await state.set_state(RegistrationFlow.ai_chat_mode)

# Обработка кнопки контактов внутри режима общения с гигачатом
@router_menu.message(RegistrationFlow.ai_chat_mode, F.text == "Контакты поддержки")
async def contact_support(message: Message):
    await message.answer(
        "Контакты для связи:\n\n"
        
        "Телефон: +79991112233\n"
        "Telegram: юзер менеджера/сотрудника\n"
        "Email: емейл@sber.ru\n\n"
        
        "Вы можете продолжить общение с ботом или вернуться в меню.",
        reply_markup=kb_ai_chat
    )


# Логика общения с гигачатом
# Бот "печатает" -> возвращает ответ -> выводит

@router_menu.message(RegistrationFlow.ai_chat_mode)
async def process_ai_chat(message: Message, state: FSMContext):
    user_text = message.text
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    ai_response = await ask_gigachat(user_text)
    await message.answer(ai_response, reply_markup=kb_ai_chat)