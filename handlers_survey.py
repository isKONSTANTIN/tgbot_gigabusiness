import os
import html
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from states import RegistrationFlow
from keyboards import *
from handlers_menu import cmd_start

router_survey = Router()
PDF_FOLDER = "pdfs"


def get_pdf(filename: str):
    path = os.path.join(PDF_FOLDER, filename)
    return FSInputFile(path)


# База данных ссылок
LINKS_DB = {
    # Счета для самозанятых
    "bank_self": {
        "СберБанк": "https://www.sberbank.ru/ru/person/bank_cards/debit",
        "Альфа": "https://alfabank.ru/everyday/debit-cards/alfacard/",
        "ВТБ": "https://www.vtb.ru/personal/karty/"
    },
    # Банки для регистрации бизнеса
    "reg_bank": {
        "СберБанк": "https://www.sberbank.ru/ru/s_m_business",
        "Альфа": "https://alfabank.ru/sme/loyalty/agent/start/rko_10000",
        "ВТБ": "https://reg.vtb.ru/"
    },
    # Эквайринг связываемый с выбором банка
    "acquiring": {
        "СберБанк": "https://www.sberbank.ru/ru/s_m_business/bankingservice/acquiring_total",
        "Альфа": "https://alfabank.ru/sme/payservice/acquiring/",
        "ВТБ": "https://www.vtb.ru/malyj-biznes/acquiring/"
    },
    # Бухгалтерия
    "accounting": {
        "Онлайн-бухгалтерия": "https://www.sberbank.ru/ru/s_m_business/nbs/accountant_portal",
        "Аутсорсинг": "https://www.sberbank.ru/ru/s_m_business/nbs/accountant_portal",
        "Штатный бухгалтер": "https://pskov.hh.ru/smb?search=бухгалтер",
        "Приходящий бухгалтер": "https://pskov.hh.ru/smb?search=бухгалтер"
    },
    # CRM системы
    "crm": {
        "SberCRM": "https://sbercrm.com/",
        "AmoCRM": "https://www.amocrm.ru/",
        "Битрикс24": "https://www.bitrix24.ru/"
    },
    # Места регистрации (общие)
    "reg_place_info": {
        "Госуслуги": "https://www.gosuslugi.ru/help/faq/business",
        "МФЦ / ФНС": "https://www.sberbank.com/ru/s_m_business/pro_business/registraciya-ip-cherez-mfc-poshagovaya-instrukciya"
    },
    # Помещение
    "premises": "https://pskov.cian.ru/commercial/",
    # Сотрудники
    "employees": "https://hh.ru/employer?hhtmFrom=main",
    # Реклама
    "ads": "https://sbermarketing.ru/?utm_source=yandex.ru&utm_medium=organic&utm_campaign=yandex.ru&utm_referrer=yandex.ru"
}


def get_link_html(category, key, text_override=None):
    """Помогает достать ссылку и вернуть красивый HTML тег <a>"""

    '''
    1. Получение данных категории (словарь или строка)
    2. Если словарь (например банк) - поиск по ключу
    3. Если строка (например помещение) - берется сама строка как ссылка
    4. Если ссылка нашлась - то формируется HTML
    5. Если ссылки нет - возвращается просто текст
    '''

    category_data = LINKS_DB.get(category)
    url = None

    if isinstance(category_data, dict):
        url = category_data.get(key)
    elif isinstance(category_data, str):
        url = category_data

    if url:
        name = text_override if text_override else key
        return f"<a href='{url}'>{name}</a>"

    return key

'''
Формат блоков опросника:

# Номер блока: N
Нажата кнопка "Назад" - состояние возвращается на предыдущий шаг;
Логика вперед: Обработка выбора на текущем шаге;
Если выбрана помощь, обработка отправки PDF и возвращение к вопросу;
Возможное ветвление (Опционально);
После выбора запись ответа на текущий шаг и вывод вопроса для следующего щага;
'''

# Блок 1.1: Опросник: Шаг 1 - название и форма регистрации

# Кнопка назад с шага "Выбор формы" -> На шаг "Ввод названия"
@router_survey.message(RegistrationFlow.waiting_for_business_name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "В главное меню":
        return await cmd_start(message, state)

    # Логика вперед (Ввод названия)
    await state.update_data(business_name=message.text)
    await message.answer(
        f"Название: <b>{html.escape(message.text)}</b>.\n\n"
        "Выберите форму регистрации:",
        parse_mode="HTML",
        reply_markup=kb_form_types
    )
    await state.set_state(RegistrationFlow.waiting_for_form_choice)


# Кнопка назад с шага "Выбора формы" -> К выбору названия
@router_survey.message(RegistrationFlow.waiting_for_form_choice, F.text == "Назад")
async def back_to_name(message: Message, state: FSMContext):
    await message.answer(
        "Вернулись назад.\n"
        "Как будет называться ваш бизнес?",
        reply_markup=kb_back_to_menu
    )
    await state.set_state(RegistrationFlow.waiting_for_business_name)


# Логика вперед (Выбор формы)

@router_survey.message(RegistrationFlow.waiting_for_form_choice)
async def process_form_choice(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "Помогите" in choice or "PDF" in choice:
        await message.answer("Подробнее о формах регистрации в файле ниже:")
        try:
            await message.answer_document(get_pdf("Форма регистрации.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Какую форму выберете?", reply_markup=kb_form_types)
        return

    # Валидация
    if choice not in ["Самозанятый", "ИП", "ООО"]:
        await message.answer("Пожалуйста, выберите вариант, используя кнопки меню.", reply_markup=kb_form_types)
        return

    await state.update_data(reg_form=choice)

    if "Самозанятый" in choice:
        await message.answer(
            f"Выбрано: {choice}.\n\n"
            f"В каком банке откроете счет?",
            reply_markup=kb_banks
        )
        await state.set_state(RegistrationFlow.waiting_for_bank_choice_self)

    elif choice in ["ИП", "ООО"]:
        await message.answer(
            f"Выбрано: {choice}.\n\n"
            f"Выберите систему налогообложения:",
            reply_markup=kb_tax_regimes
        )
        await state.set_state(RegistrationFlow.waiting_for_tax_choice)
    else:
        await message.answer("Используйте кнопки.", reply_markup=kb_form_types)


# Блок 1.2: Самозанятые

async def finalize_self_employed(message: Message, state: FSMContext):
    data = await state.get_data()
    name = html.escape(data.get('business_name', 'Мой бизнес'))
    bank_choice = data.get('chosen_bank', 'СберБанк')

    # Получаем ссылку на банк
    bank_link = get_link_html("bank_self", bank_choice)

    text = (
        f"<b>План запуска для: {name}</b>\n\n"
        
        "1. <b>Регистрация</b>: Скачайте приложение «Мой налог».\n"
        "2. <b>Налоги</b>: НПД (платите % с пришедших денег).\n"
        f"3. <b>Счет</b>: {bank_link}.\n\n"
        
        "Для более подробной информации вы можете перейти по ссылкам в плане. "
        "<b>Также ниже приведены полезные материалы:</b>\n"
        f"{bank_link} (Оформить карту)\n"
        f"<a href='https://l.npd.nalog.ru/'>Скачать «Мой налог»</a>\n\n"
        
        "Ваш бизнес готов к старту! Удачи!\n"
        "Если остались вопросы — спросите у GigaChat в меню."
    )

    # метод disable_web_page_preview=True чтобы не было превьюшек ссылок
    await message.answer(text, parse_mode="HTML", reply_markup=kb_final, disable_web_page_preview=True)
    await state.set_state(RegistrationFlow.waiting_for_support_question)


# Кнопка назад с шага "Выбора банка" (самозанятый) -> К выбору формы
@router_survey.message(RegistrationFlow.waiting_for_bank_choice_self, F.text == "Назад")
async def back_to_form_self(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору формы.", reply_markup=kb_form_types)
    await state.set_state(RegistrationFlow.waiting_for_form_choice)


# Логика вперед: Выбор банка самозанятого
@router_survey.message(RegistrationFlow.waiting_for_bank_choice_self)
async def process_bank_self(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice or "Как выбрать" in choice:
        await message.answer("Подробнее о выборе счета в файле ниже:")
        try:
            await message.answer_document(get_pdf("Счет для самозанятого.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Какой банк выберете?", reply_markup=kb_banks)
        return

    # Валидация
    if choice not in ["СберБанк", "Альфа", "ВТБ", "Другой"]:
        await message.answer("Пожалуйста, выберите банк из списка.", reply_markup=kb_banks)
        return

    await state.update_data(chosen_bank=choice)
    await finalize_self_employed(message, state)


# Блок 2: ИП/ООО - Налоги

# Кнопка назад с шага "выбор налогов" -> К выбору формы
@router_survey.message(RegistrationFlow.waiting_for_tax_choice, F.text == "Назад")
async def back_to_form_tax(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору формы.", reply_markup=kb_form_types)
    await state.set_state(RegistrationFlow.waiting_for_form_choice)


# Логика вперед: Выбор системы налогообложения
@router_survey.message(RegistrationFlow.waiting_for_tax_choice)
async def process_tax_choice(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice or "Что выбрать" in choice:
        await message.answer("Сравнение налоговых режимов в файле ниже:")
        try:
            await message.answer_document(get_pdf("Налоговый режим.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Что выберете?", reply_markup=kb_tax_regimes)
        return

    # Валидация
    valid_taxes = ["УСН (Доходы)", "УСН (Доходы-Расходы)", "Патент", "ОСНО", "АУСН"]
    if choice not in valid_taxes:
        await message.answer("Пожалуйста, выберите налоговый режим кнопкой.", reply_markup=kb_tax_regimes)
        return

    await state.update_data(tax_system=choice)
    await message.answer("Теперь укажите код деятельности (ОКВЭД):", reply_markup=kb_okved_top)
    await state.set_state(RegistrationFlow.waiting_for_okved_selection)


# Блок 3: ОКВЭД

# Кнопка назад с шага "ОКВЭД (выбор)" -> К выбору налогов
@router_survey.message(RegistrationFlow.waiting_for_okved_selection, F.text == "Назад")
async def back_to_tax(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору налогов.", reply_markup=kb_tax_regimes)
    await state.set_state(RegistrationFlow.waiting_for_tax_choice)


# Логика вперед: Выбор из списка или нажатие кнопки "Ввести вручную"
@router_survey.message(RegistrationFlow.waiting_for_okved_selection)
async def process_okved(message: Message, state: FSMContext):
    text = message.text

    # Справка (PDF)
    if "PDF" in text or "Что такое" in text:
        await message.answer("Справочник по кодам ОКВЭД в файле ниже:")
        try:
            await message.answer_document(get_pdf("ОКВЭД.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Выберите вариант:", reply_markup=kb_okved_top)
        return

    # Если нажато "Ввести код вручную" -> Переход в режим ввода
    if text == "Ввести код вручную":
        await message.answer(
            "<b>Напишите ваш основной вид деятельности.</b>\n\n"
            "Например: <i>Разработка ПО</i> или код <i>62.01</i>",
            parse_mode="HTML",
            reply_markup=kb_input_nav  # Клавиатура "Назад / Меню"
        )
        await state.set_state(RegistrationFlow.waiting_for_okved_custom)
        return

    # Если выбрана кнопка с готовым вариантом
    await state.update_data(okved=text)
    await message.answer(
        f"Выбранный ОКВЭД: <b>{html.escape(text)}</b>.\n\n"
        "Как планируете подавать документы?",
        parse_mode="HTML", reply_markup=kb_reg_places
    )
    await state.set_state(RegistrationFlow.waiting_for_reg_place_choice)


# Подветка: Ручной ввод ОКВЭД

# Кнопка назад с шага "Ввод вручную" -> Обратно к списку ОКВЭД
@router_survey.message(RegistrationFlow.waiting_for_okved_custom, F.text == "Назад")
async def back_to_okved_list(message: Message, state: FSMContext):
    await message.answer("Выберите сферу из списка:", reply_markup=kb_okved_top)
    await state.set_state(RegistrationFlow.waiting_for_okved_selection)


# Логика вперед: Обработка введенного текста
@router_survey.message(RegistrationFlow.waiting_for_okved_custom)
async def process_okved_custom(message: Message, state: FSMContext):
    user_input = message.text

    # Сохранение инпута и следующий шаг
    await state.update_data(okved=user_input)
    await message.answer(
        f"ОКВЭД принят: <b>{html.escape(user_input)}</b>.\n\n"
        "Как планируете подавать документы?",
        parse_mode="HTML", reply_markup=kb_reg_places
    )
    await state.set_state(RegistrationFlow.waiting_for_reg_place_choice)


# Блок 4: Место регистрации

# Кнопка назад с шага "Место регистрации" -> К ОКВЭД
@router_survey.message(RegistrationFlow.waiting_for_reg_place_choice, F.text == "Назад")
async def back_to_okved(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору ОКВЭД.", reply_markup=kb_okved_top)
    await state.set_state(RegistrationFlow.waiting_for_okved_selection)


# Логика вперед: Выбор места
@router_survey.message(RegistrationFlow.waiting_for_reg_place_choice)
async def process_reg_place(message: Message, state: FSMContext):
    place = message.text

    # Справка (PDF)
    if "PDF" in place or "Где лучше" in place:
        await message.answer("Сравнение способов регистрации в файле ниже:")
        try:
            await message.answer_document(get_pdf("Выбор места регистрации бизнеса.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Какой способ выберете?", reply_markup=kb_reg_places)
        return

    # Валидация
    if place not in ["Через Банк (Онлайн)", "Госуслуги", "МФЦ / ФНС"]:
        await message.answer("Выберите способ регистрации из меню.", reply_markup=kb_reg_places)
        return

    await state.update_data(reg_place=place)

    # Ветвление: Если выбран "Банк", то уточняется какой
    if "Банк" in place:
        await message.answer("Через какой банк?", reply_markup=kb_banks)
        await state.set_state(RegistrationFlow.waiting_for_reg_bank_choice)
    # Иначе переход к Кассе
    else:
        await message.answer("Принято. Какую кассу выберете?", reply_markup=kb_kassa_types)
        await state.set_state(RegistrationFlow.waiting_for_kassa_choice)


# Подветка: Выбор банка для регистрации

# Кнопка назад с шага "Банк регистрации" -> К выбору места
@router_survey.message(RegistrationFlow.waiting_for_reg_bank_choice, F.text == "Назад")
async def back_to_place(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору способа регистрации.", reply_markup=kb_reg_places)
    await state.set_state(RegistrationFlow.waiting_for_reg_place_choice)


# Логика вперед: Выбор банка
@router_survey.message(RegistrationFlow.waiting_for_reg_bank_choice)
async def process_reg_bank(message: Message, state: FSMContext):
    bank = message.text

    # Справка (PDF)
    if "PDF" in bank:
        await message.answer("Подробнее о том, как выбрать банк для регистрации в файле ниже:")
        try:
            await message.answer_document(get_pdf("Выбор банка для регистрации бизнеса.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Выберите банк:", reply_markup=kb_banks)
        return

    # Валидация
    if bank not in ["СберБанк", "Альфа", "ВТБ", "Другой"]:
        await message.answer("Выберите банк из предложенных.", reply_markup=kb_banks)
        return

    await state.update_data(reg_bank_name=bank)
    await message.answer(f"Банк: <b>{html.escape(bank)}</b>.\n\n"
                         "Какую кассу выберете?",
                         parse_mode="HTML", reply_markup=kb_kassa_types)
    await state.set_state(RegistrationFlow.waiting_for_kassa_choice)


# Блок 5: Касса

# Кнопка назад с шага "Кассы" -> Назад на банк или мфц
@router_survey.message(RegistrationFlow.waiting_for_kassa_choice, F.text == "Назад")
async def back_from_kassa(message: Message, state: FSMContext):
    data = await state.get_data()
    reg_place = data.get("reg_place", "")

    # Проверка, куда вернуть пользователя
    if "Банк" in reg_place:
        await message.answer("Вернулись к выбору банка регистрации.", reply_markup=kb_banks)
        await state.set_state(RegistrationFlow.waiting_for_reg_bank_choice)
    else:
        await message.answer("Вернулись к выбору способа регистрации.", reply_markup=kb_reg_places)
        await state.set_state(RegistrationFlow.waiting_for_reg_place_choice)


# Логика вперед: Выбор кассы
@router_survey.message(RegistrationFlow.waiting_for_kassa_choice)
async def process_kassa(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice or "помощь" in choice:
        await message.answer("Подробнее про кассы и эквайринг в файле ниже:")
        try:
            await message.answer_document(get_pdf("Касса и эквайринг.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Что выберете?", reply_markup=kb_kassa_types)
        return

    # Валидация
    valid_kassa = ["Офлайн касса", "Онлайн касса", "Гибрид (Оба варианта)"]
    if choice not in valid_kassa:
        await message.answer("Выберите тип кассы кнопкой.", reply_markup=kb_kassa_types)
        return

    await state.update_data(kassa_type=choice)

    # Переход к эквайрингу
    await message.answer(
        "Касса записана.\n"
        "Планируете принимать оплату картами (эквайринг)?",
        reply_markup=kb_acquiring_decision
    )
    await state.set_state(RegistrationFlow.waiting_for_acquiring_decision)


# Блок 6: Эквайринг

# Кнопка назад с шага "Эквайринг" (решение) -> К Кассе
@router_survey.message(RegistrationFlow.waiting_for_acquiring_decision, F.text == "Назад")
async def back_to_kassa_from_acq(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору кассы.", reply_markup=kb_kassa_types)
    await state.set_state(RegistrationFlow.waiting_for_kassa_choice)


# Логика вперед: Решение по эквайрингу
@router_survey.message(RegistrationFlow.waiting_for_acquiring_decision)
async def process_acquiring_dec(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice:
        await message.answer("Что такое эквайринг описали в файле ниже:")
        try:
            await message.answer_document(get_pdf("Касса и эквайринг.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Нужен ли эквайринг?", reply_markup=kb_acquiring_decision)
        return

    # Валидация
    if choice not in ["Да, нужно", "Нет, не нужно"]:
        await message.answer("Используйте кнопки.", reply_markup=kb_acquiring_decision)
        return

    if "Да" in choice:
        await message.answer("Какого партнера по эквайрингу выберете?", reply_markup=kb_banks)
        await state.set_state(RegistrationFlow.waiting_for_acquiring_bank)
    else:
        # Если не нужен -> переход к РКО
        await state.update_data(acquiring_bank="Не нужен")
        await message.answer("Понял. Теперь выберите банк для расчетного счета (РКО):", reply_markup=kb_banks)
        await state.set_state(RegistrationFlow.waiting_for_rko_choice)


# Кнопка назад от шага "Выбор банка для эквайринга" -> К Решению
@router_survey.message(RegistrationFlow.waiting_for_acquiring_bank, F.text == "Назад")
async def back_to_acq_dec(message: Message, state: FSMContext):
    await message.answer("Вернулись назад. Нужен ли эквайринг?", reply_markup=kb_acquiring_decision)
    await state.set_state(RegistrationFlow.waiting_for_acquiring_decision)


# Логика вперед: Выбор банка эквайринга
@router_survey.message(RegistrationFlow.waiting_for_acquiring_bank)
async def process_acquiring_bank(message: Message, state: FSMContext):
    bank = message.text

    # Справка (PDF)
    if "PDF" in bank:
        await message.answer("Подробнее о том, как выбрать банк для регистрации в файле ниже:")
        try:
            await message.answer_document(get_pdf("Выбор банка для регистрации бизнеса.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Выберите банк:", reply_markup=kb_banks)
        return

    # Валидация
    if bank not in ["СберБанк", "Альфа", "ВТБ", "Другой"]:
        await message.answer("Выберите банк из списка.", reply_markup=kb_banks)
        return

    await state.update_data(acquiring_bank=bank)

    # Переход к счету РКО
    await message.answer(
        f"Эквайринг: {bank}.\n"
        "Теперь выберите банк для расчетного счета (РКО).\n"
        "Рекомендуем открывать счет там же, где эквайринг.",
        reply_markup=kb_banks
    )
    await state.set_state(RegistrationFlow.waiting_for_rko_choice)


# Блок 7: Расчетный счет (РКО)

# Кнопка назад от шага "Расчетный счет РКО" -> К Эквайрингу (решению)
@router_survey.message(RegistrationFlow.waiting_for_rko_choice, F.text == "Назад")
async def back_to_acquiring(message: Message, state: FSMContext):
    await message.answer("Вернулись к вопросу об эквайринге.", reply_markup=kb_acquiring_decision)
    await state.set_state(RegistrationFlow.waiting_for_acquiring_decision)


# Логика вперед: Выбор РКО
@router_survey.message(RegistrationFlow.waiting_for_rko_choice)
async def process_rko(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice:
        await message.answer("Справка о РКО в файле ниже:")
        try:
            await message.answer_document(get_pdf("Расчетный счет.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Где откроете счет?", reply_markup=kb_banks)
        return

    # Валидация
    if choice not in ["СберБанк", "Альфа", "ВТБ", "Другой"]:
        await message.answer("Выберите банк из списка.", reply_markup=kb_banks)
        return

    await state.update_data(rko_bank=choice)
    await message.answer("Планируете нанимать сотрудников?", reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_employees_decision)


# Блок 8: Сотрудники

# Кнопка назад с шага: "Сотрудники" -> К РКО
@router_survey.message(RegistrationFlow.waiting_for_employees_decision, F.text == "Назад")
async def back_to_rko(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору банка для счета.", reply_markup=kb_banks)
    await state.set_state(RegistrationFlow.waiting_for_rko_choice)


# Логика вперед: Решение по сотрудникам
@router_survey.message(RegistrationFlow.waiting_for_employees_decision)
async def process_employees(message: Message, state: FSMContext):
    # Валидация
    if message.text not in ["Да", "Нет"]:
        await message.answer("Пожалуйста, нажмите Да или Нет.", reply_markup=kb_yes_no)
        return
    await state.update_data(need_employees=message.text)
    await message.answer("Кто будет вести бухгалтерию?", reply_markup=kb_accounting_types)
    await state.set_state(RegistrationFlow.waiting_for_accounting_choice)


# Блок 9: Бухгалтерия

# Кнопка назад с шага: "Бухгалтерия" -> К Сотрудникам
@router_survey.message(RegistrationFlow.waiting_for_accounting_choice, F.text == "Назад")
async def back_to_employees(message: Message, state: FSMContext):
    await message.answer("Вернулись к вопросу о сотрудниках.", reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_employees_decision)


# Логика вперед: Выбор бухгалтерии
@router_survey.message(RegistrationFlow.waiting_for_accounting_choice)
async def process_accounting(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice:
        await message.answer("Подробнее о видах бухгалтерии в файле ниже:")
        try:
            await message.answer_document(get_pdf("Бухгалтерия.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Как будете вести учет?", reply_markup=kb_accounting_types)
        return

    # Валидация
    valid_acc = ["Онлайн-бухгалтерия", "Аутсорсинг", "Штатный бухгалтер", "Приходящий бухгалтер"]
    if choice not in valid_acc:
        await message.answer("Выберите тип бухгалтерии из меню.", reply_markup=kb_accounting_types)
        return

    await state.update_data(accounting_type=choice)
    await message.answer("Нужно ли вам коммерческое помещение?", reply_markup=kb_premises)
    await state.set_state(RegistrationFlow.waiting_for_premises_decision)


# Блок 10: Помещение

# Кнопка назад с шага: "Помещение" -> К Бухгалтерии
@router_survey.message(RegistrationFlow.waiting_for_premises_decision, F.text == "Назад")
async def back_to_accounting(message: Message, state: FSMContext):
    await message.answer("Вернулись к выбору бухгалтерии.", reply_markup=kb_accounting_types)
    await state.set_state(RegistrationFlow.waiting_for_accounting_choice)


# Логика вперед: Решение по помещению
@router_survey.message(RegistrationFlow.waiting_for_premises_decision)
async def process_premises(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice:
        await message.answer("Справочник по выбору помещения в файле ниже:")
        try:
            await message.answer_document(get_pdf("Помещение.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Нужно ли помещение?", reply_markup=kb_premises)
        return

    # Валидация
    if choice not in ["Да, нужно", "Нет, не нужно"]:
        await message.answer("Выберите вариант кнопкой.", reply_markup=kb_premises)
        return

    await state.update_data(need_premises=choice)
    await message.answer("Нужна ли вам CRM-система?", reply_markup=kb_crm_decision)
    await state.set_state(RegistrationFlow.waiting_for_crm_decision)


# Блок 11: CRM системы

# Кнопка назад с шага: "CRM (решение)" -> К Помещению
@router_survey.message(RegistrationFlow.waiting_for_crm_decision, F.text == "Назад")
async def back_to_premises(message: Message, state: FSMContext):
    await message.answer("Вернулись к вопросу о помещении.", reply_markup=kb_premises)
    await state.set_state(RegistrationFlow.waiting_for_premises_decision)


# Логика вперед: Решение по CRM
@router_survey.message(RegistrationFlow.waiting_for_crm_decision)
async def process_crm_dec(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice:
        await message.answer("Подробнее о том, зачем нужна CRM в файле ниже:")
        try:
            await message.answer_document(get_pdf("Выбор CRM.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Нужна ли CRM?", reply_markup=kb_crm_decision)
        return

    # Валидация
    if choice not in ["Выбрать CRM", "Не нужна"]:
        await message.answer("Используйте кнопки меню.", reply_markup=kb_crm_decision)
        return

    if "Выбрать CRM" in choice:
        await message.answer("Какую систему выберете?", reply_markup=kb_crm_list)
        await state.set_state(RegistrationFlow.waiting_for_crm_selection)
    else:
        await state.update_data(crm_system="Не нужна")
        await message.answer("Будете запускать рекламу?", reply_markup=kb_ads)
        await state.set_state(RegistrationFlow.waiting_for_ads_decision)


# Кнопка назад с шага: "CRM (список)" -> К CRM (решение)
@router_survey.message(RegistrationFlow.waiting_for_crm_selection, F.text == "Назад")
async def back_to_crm_dec(message: Message, state: FSMContext):
    await message.answer("Вернулись назад.", reply_markup=kb_crm_decision)
    await state.set_state(RegistrationFlow.waiting_for_crm_decision)


# Логика вперед: Выбор конкретной CRM
@router_survey.message(RegistrationFlow.waiting_for_crm_selection)
async def process_crm_sel(message: Message, state: FSMContext):
    # Валидация
    if message.text not in ["SberCRM", "AmoCRM", "Битрикс24"]:
        await message.answer("Выберите CRM из списка.", reply_markup=kb_crm_list)
        return
    await state.update_data(crm_system=message.text)
    await message.answer("CRM выбрана. Будете запускать рекламу?", reply_markup=kb_ads)
    await state.set_state(RegistrationFlow.waiting_for_ads_decision)


# Блок 12: Реклама и финальное сообщение

# Кнопка назад с шага: "Реклама" -> К CRM
@router_survey.message(RegistrationFlow.waiting_for_ads_decision, F.text == "Назад")
async def back_to_crm_general(message: Message, state: FSMContext):
    await message.answer("Вернулись к блоку CRM.", reply_markup=kb_crm_decision)
    await state.set_state(RegistrationFlow.waiting_for_crm_decision)


# Логика вперед: Реклама и генерация итога
@router_survey.message(RegistrationFlow.waiting_for_ads_decision)
async def process_ads(message: Message, state: FSMContext):
    choice = message.text

    # Справка (PDF)
    if "PDF" in choice:
        await message.answer("Подробее о каналах рекламы в файле ниже:")
        try:
            await message.answer_document(get_pdf("Реклама.pdf"))
        except:
            await message.answer("Файл не найден.")
        await message.answer("Нужна ли реклама?", reply_markup=kb_ads)
        return

    # Валидация
    if choice not in ["Да, планирую", "Нет, не планирую"]:
        await message.answer("Пожалуйста, ответьте Да или Нет.", reply_markup=kb_ads)
        return

    await state.update_data(need_ads=choice)

    # Генерация итога
    data = await state.get_data()

    # Сбор и экранирование данных
    name = html.escape(data.get('business_name', 'Бизнес'))
    form = html.escape(data.get('reg_form', 'Нет'))
    tax = html.escape(data.get('tax_system', 'Нет'))
    okved = html.escape(data.get('okved', 'Нет'))

    # Регистрация
    reg_place_val = data.get('reg_place', 'Нет')
    reg_place_link = get_link_html("reg_place_info", reg_place_val)

    reg_bank_val = data.get('reg_bank_name', 'Нет')
    reg_bank_link = get_link_html("reg_bank", reg_bank_val)

    kassa = html.escape(data.get('kassa_type', 'Нет'))

    # Эквайринг (Вывод в общем плане)
    acq_val = data.get('acquiring_bank', 'Не нужен')
    if acq_val == "Не нужен":
        acq_text = "Не нужен"
        acq_link = "Нет"
    else:
        # Если выбран банк, делаем ссылку. Берем ссылки из категории 'acquiring'
        acq_text = html.escape(acq_val)
        acq_link = get_link_html("acquiring", acq_val, text_override=f"Подключить ({acq_val})")

    # РКО
    rko_val = data.get('rko_bank', 'Нет')
    rko_link = get_link_html("bank_self", rko_val)  # Используем базу банков

    # Эквайринг (Вывод в полезных материалах)
    acquiring_link = get_link_html("acquiring", rko_val, text_override=f"Эквайринг ({rko_val})")

    # Сотрудники
    empl_val = data.get('need_employees', 'Нет')
    if "Да" in empl_val: empl = get_link_html("employees", "Да")
    else: empl = html.escape(empl_val)

    # Бухгалтерия
    acc_val = data.get('accounting_type', 'Нет')
    acc_link = get_link_html("accounting", acc_val)

    # Помещение
    prem_val = data.get('need_premises', 'Нет')
    prem_link = get_link_html("premises", "Cian.ru") if "Да" in prem_val else "Нет"

    # CRM
    crm_val = data.get('crm_system', 'Нет')
    crm_link = get_link_html("crm", crm_val)

    # Реклама
    ads_val = data.get('need_ads', 'Нет')
    ads_link = get_link_html("ads", "SberMarketing") if "Да" in ads_val else "Нет"

    final_msg = (
        f"<b>Итоговый план для: {name}</b>\n\n"
        
        f"1. Форма: {form}\n"
        f"2. Налог: {tax}\n"
        f"3. ОКВЭД: {okved}\n"
        f"4. Регистрация: {reg_place_link} (Банк: {reg_bank_link})\n"
        f"5. Касса: {kassa}\n"
        f"6. Эквайринг: {acq_text}\n"
        f"7. Счет (РКО): {rko_link}\n"
        f"8. Сотрудники: {empl}\n"
        f"9. Бухгалтерия: {acc_link}\n"
        f"10. Помещение: {prem_link}\n"
        f"11. CRM: {crm_link}\n"
        f"12. Реклама: {ads_link}\n\n"
        
        "Для более подробной информации вы можете перейти по ссылкам в плане. "
        "<b>Также ниже приведены полезные материалы:</b>\n"
        f"{acquiring_link}\n"
        f"<a href='https://www.sberbank.ru/ru/s_m_business'>СберБизнес Старт</a>\n\n"
        
        "Удачи в бизнесе!\n"
        "Если остались вопросы — спросите у GigaChat в меню."
    )

    await message.answer(final_msg, parse_mode="HTML", reply_markup=kb_final, disable_web_page_preview=True)
    await state.set_state(RegistrationFlow.waiting_for_support_question)


# Конечные кнопки

@router_survey.message(RegistrationFlow.waiting_for_support_question)
async def support_handler(message: Message, state: FSMContext):

    if "Вопросов нет" in message.text:
        await message.answer("Рад помочь! Возвращаю вас в главное меню.",
        reply_markup=kb_main_menu
        )
        await state.clear()

    else:
        await message.answer(
            "Чтобы задать вопрос, перейдите в <b>Главное меню</b> и выберите <b>«Спросить у GigaChat»</b>.",
            parse_mode="HTML", reply_markup=kb_main_menu
        )
        await state.clear()