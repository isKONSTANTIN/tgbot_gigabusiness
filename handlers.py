from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command

from states import RegistrationFlow
from keyboards import (kb_yes_no, kb_form_types, kb_tax_regimes, kb_banks, kb_okved_top, kb_reg_places,
                       kb_kassa_types, kb_accounting_types, kb_crm_list, kb_final, kb_restart)

router = Router()

# Структура бота, как и его логики поделена на блоки кода.
# Блок может заканчиваться новым вопросом, а в следующем за ним начинаться логика ветвления.

# To do: вероятно стоит внедрить перманентную кнопку "В главное меню"
# Некоторые сценарии заглушены, не доделаны, или нуждаются в переосмыслении.
# Надлежащего наполнения и пояснения к вопросам, по моему мнению, еще нет.

# 1. Старт и название компании

@router.message(Command("start"))
async def cmd_start(message: Message, state: F):
    await message.answer(
        "Привет! Я бизнес-ассистент. Вы хотите создать свой бизнес?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_start_decision)


@router.message(RegistrationFlow.waiting_for_start_decision, F.text.lower() == "да")
async def process_start_yes(message: Message, state: F):
    await message.answer(
        "Отлично! Как будет называться ваш бизнес?\n"
        "(Напишите название текстом)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationFlow.waiting_for_business_name)


@router.message(RegistrationFlow.waiting_for_start_decision, F.text.lower() == "нет")
async def process_start_no(message: Message, state: F):
    await message.answer("Хорошо, если надумаете — пишите /start")
    await state.clear()


@router.message(RegistrationFlow.waiting_for_business_name)
async def process_name(message: Message, state: F):
    user_text = message.text
    await state.update_data(business_name=user_text)

    await message.answer(
        f"✅ Отлично, название: \"{user_text}\"!\n\n"
        "Вы знаете, какая форма регистрации вам нужна\n"
        "(Самозанятость, ИП, ООО)?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_form_knowledge)



# 2. Выбор формы регистрации

@router.message(RegistrationFlow.waiting_for_form_knowledge, F.text.lower() == "да")
async def form_know_yes(message: Message, state: F):
    await message.answer("Выберите форму регистрации:", reply_markup=kb_form_types)
    await state.set_state(RegistrationFlow.waiting_for_form_choice)


@router.message(RegistrationFlow.waiting_for_form_knowledge, F.text.lower() == "нет")
async def form_know_no(message: Message, state: F):
    info_text = (
        "Описание:\n"
        "Самозанятый: доход до 2.4 млн/год, без сотрудников.\n"
        "ИП: можно нанимать людей, простой вывод денег.\n"
        "ООО: для партнерства, сложнее отчетность.\n\n"
        "Что выберете?"
    )
    await message.answer(info_text, parse_mode="Markdown", reply_markup=kb_form_types)
    await state.set_state(RegistrationFlow.waiting_for_form_choice)


# 3. Логика ветвления регистраций (Самозанятость или ИП/ООО)

@router.message(RegistrationFlow.waiting_for_form_choice)
async def process_form_choice(message: Message, state: F):
    user_choice = message.text
    await state.update_data(reg_form=user_choice) # Сохранение выбора

    # Ветка самозанятости
    if "Самозанятый" in user_choice:
        text = (
            "✅ Выбрана самозанятость.\n\n"
            "Это налог НПД. Ставки: 4% с физлиц, 6% с юрлиц.\n"
            "Регистрация происходит в приложении «Мой налог».\n\n"
            "У вас уже есть счет для приема денег?"
        )
        await message.answer(text, reply_markup=kb_yes_no)
        await state.set_state(RegistrationFlow.waiting_for_account_existence)

    # Ветка ИП или ООО
    elif user_choice in ["ИП", "ООО"]:
        await message.answer(
            f"✅ Выбрано {user_choice}.\n\n"
            "Вы знаете, какой налоговый режим вам подойдет?",
            reply_markup=kb_yes_no
        )
        await state.set_state(RegistrationFlow.waiting_for_tax_knowledge)

    else:
        await message.answer("Выберите ИП, ООО или Самозанятость кнопками ниже:", reply_markup=kb_form_types)


# 4. Укороченная ветка для самозанятых

async def finalize_self_employed(message: Message, state: F):
    data = await state.get_data()
    name = data.get('business_name', 'Мой бизнес')
    bank = data.get('chosen_bank', 'Уже есть')

    # Формирование сообщения
    final_text = (
        f"План запуска для: {name}\n\n"
        "1. Регистрация: Скачайте приложение «Мой налог» или используйте сервис «Свое дело» в СберБанк Онлайн.\n"
        "2. Налоги: НПД (4% с физлиц / 6% с юрлиц). Чеки формируете в приложении.\n"
        f"3. Счет: {bank}.\n\n"
        "Ваш бизнес готов к старту! Удачи!"
    )

    await message.answer(final_text, parse_mode="Markdown")
    await message.answer("Остались ли у вас вопросы?", reply_markup=kb_final)
    await state.set_state(RegistrationFlow.waiting_for_support_question)


@router.message(RegistrationFlow.waiting_for_account_existence, F.text.lower() == "нет")
async def account_no(message: Message, state: F):
    text = "Где хотите открыть счет?"
    await message.answer(text, reply_markup=kb_banks)
    await state.set_state(RegistrationFlow.waiting_for_bank_choice)


@router.message(RegistrationFlow.waiting_for_account_existence, F.text.lower() == "да")
async def account_yes(message: Message, state: F):
    await state.update_data(has_account="Да")
    await finalize_self_employed(message, state)

@router.message(RegistrationFlow.waiting_for_bank_choice)
async def process_bank_choice(message: Message, state: F):
    bank = message.text
    await state.update_data(chosen_bank=bank)

    if "Сбер" in bank:
        await message.answer("Отличный выбор!")
    else:
        await message.answer(f"Принято: {bank}.")

    await finalize_self_employed(message, state)


# 5. Ветка для ИП или ООО: Налоги
# Если пользователь не самозанятый, продолжается длинный сценарий

@router.message(RegistrationFlow.waiting_for_tax_knowledge, F.text.lower() == "нет")
async def tax_info(message: Message, state: F):
    info = (
        "Коротко о режимах:\n"
        "УСН: Платите % с дохода.\n"
        "Патент: Фикс сумма за год (только ИП).\n"
        "ОСНО: С НДС (сложно).\n"
        "АУСН: Автоматика.\n\n"
        "Что выберете?"
    )
    await message.answer(info, parse_mode="Markdown", reply_markup=kb_tax_regimes)
    await state.set_state(RegistrationFlow.waiting_for_tax_choice)


@router.message(RegistrationFlow.waiting_for_tax_knowledge, F.text.lower() == "да")
async def tax_ask_choice(message: Message, state: F):
    await message.answer("Отлично! Какой режим выбираете?", reply_markup=kb_tax_regimes)
    await state.set_state(RegistrationFlow.waiting_for_tax_choice)


@router.message(RegistrationFlow.waiting_for_tax_choice)
async def process_tax_choice(message: Message, state: F):
    await state.update_data(tax_system=message.text)

    await message.answer(
        "✅ Налоговый режим записан!\n\n"
        "Вы знаете свой код ОКВЭД?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_okved_knowledge)

# 6. Выбор или заполнение ОКВЭД

@router.message(RegistrationFlow.waiting_for_okved_knowledge, F.text.lower() == "нет")
async def okved_info(message: Message, state: F):
    text = (
        "Что такое ОКВЭД?\n"
        "Это цифровой код, который говорит государству, чем именно вы занимаетесь.\n"
        "Например:\n"
        "— 62.01 Разработка ПО\n"
        "— 47.19 Торговля в магазине\n\n"
        "Выберите вашу сферу из представленных, или впишите свой код:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=kb_okved_top)
    await state.set_state(RegistrationFlow.waiting_for_okved_selection)


@router.message(RegistrationFlow.waiting_for_okved_knowledge, F.text.lower() == "да")
async def okved_ask(message: Message, state: F):
    await message.answer(
        "Отлично! Напишите ваш код цифрами или выберите сферу из списка:",
        reply_markup=kb_okved_top
    )
    await state.set_state(RegistrationFlow.waiting_for_okved_selection)


@router.message(RegistrationFlow.waiting_for_okved_selection)
async def process_okved(message: Message, state: F):
    chosen_okved = message.text
    await state.update_data(okved=chosen_okved)

    await message.answer(
        f"✅ Принято. Сфера деятельности: {chosen_okved}.\n\n"
        "Следующий важный шаг: Регистрация бизнеса.\n"
        "Вы знаете, где и как подавать документы на регистрацию?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_reg_place_knowledge)


# 7. Место регистрации

@router.message(RegistrationFlow.waiting_for_reg_place_knowledge, F.text.lower() == "нет")
async def reg_place_no(message: Message, state: F):
    text = (
        "Есть несколько способов подать документы:\n"
        "1. ФНС / МФЦ: Нужно идти лично, платить госпошлину (до 4000₽).\n"
        "2. Госуслуги: Нужна электронная подпись КЭП и настройка ПК.\n"
        "3. Через банк: Бесплатно и онлайн.\n\n"
        "Какой способ выберете?"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=kb_reg_places)
    await state.set_state(RegistrationFlow.waiting_for_reg_place_choice)


@router.message(RegistrationFlow.waiting_for_reg_place_knowledge, F.text.lower() == "да")
async def reg_place_yes(message: Message, state: F):
    await message.answer(
        "Отлично! Тогда выберите предпочтительный способ из списка:",
        reply_markup=kb_reg_places
    )
    await state.set_state(RegistrationFlow.waiting_for_reg_place_choice)


@router.message(RegistrationFlow.waiting_for_reg_place_choice)
async def process_reg_place(message: Message, state: F):
    place = message.text
    await state.update_data(reg_place=place)

    if "Банк" in place:
        await message.answer(
            "При регистрации через банк важно выбрать надежного партнера.\n"
            "Вы знаете, в каком банке хотите регистрировать бизнес?",
            reply_markup=kb_yes_no
        )
        await state.set_state(RegistrationFlow.waiting_for_reg_bank_knowledge)
    elif place in ["МФЦ", "Госуслуги"]:
        await message.answer(
            f"Принято: {place}.\n\n"
            "Следующий вопрос: Онлайн-касса.\n"
            "Вы знаете, какая касса нужна вашему бизнесу?",
            reply_markup=kb_yes_no
        )
        await state.set_state(RegistrationFlow.waiting_for_kassa_knowledge)
    else:
        await message.answer("Выберите вариант кнопкой.", reply_markup=kb_reg_places)


# Выбор банка для регистрации

@router.message(RegistrationFlow.waiting_for_reg_bank_knowledge, F.text.lower() == "нет")
async def reg_bank_promo(message: Message, state: F):
    text = "Какой банк выберете?"
    await message.answer(text, parse_mode="Markdown", reply_markup=kb_banks)
    await state.set_state(RegistrationFlow.waiting_for_reg_bank_choice)


@router.message(RegistrationFlow.waiting_for_reg_bank_knowledge, F.text.lower() == "да")
async def reg_bank_ask(message: Message, state: F):
    await message.answer("Отлично, выберите банк из списка:", reply_markup=kb_banks)
    await state.set_state(RegistrationFlow.waiting_for_reg_bank_choice)


@router.message(RegistrationFlow.waiting_for_reg_bank_choice)
async def process_reg_bank_choice(message: Message, state: F):
    bank = message.text
    await state.update_data(reg_bank_name=bank)

    msg = "Отличный выбор!" if "Сбер" in bank else f"Хорошо, выбран {bank}."
    await message.answer(
        f"✅ {msg}\n\n"
        "Теперь перейдем к оборудованию.\n"
        "Вы знаете, какая касса нужна для вашего бизнеса?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_kassa_knowledge)


# 8. Выбор кассы

@router.message(RegistrationFlow.waiting_for_kassa_knowledge, F.text.lower() == "нет")
async def kassa_info(message: Message, state: F):
    text = (
        "Кассы бывают разные:\n"
        "Офлайн касса: Физический аппарат.\n"
        "Онлайн касса: Облачный сервис.\n"
        "Гибрид: И то, и другое.\n\n"
        "Что подойдет вам?"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=kb_kassa_types)
    await state.set_state(RegistrationFlow.waiting_for_kassa_choice)


@router.message(RegistrationFlow.waiting_for_kassa_knowledge, F.text.lower() == "да")
async def kassa_ask(message: Message, state: F):
    await message.answer("Выберите тип кассы:", reply_markup=kb_kassa_types)
    await state.set_state(RegistrationFlow.waiting_for_kassa_choice)


@router.message(RegistrationFlow.waiting_for_kassa_choice)
async def process_kassa_choice(message: Message, state: F):
    kassa = message.text
    await state.update_data(kassa_type=kassa)

    await message.answer(
        f"✅ Касса выбрана: {kassa}.\n\n"
        "Теперь про деньги. Для бизнеса нужен расчетный счет (РКО).\n"
        "Вы знаете, в каком банке выгоднее всего открыть счет?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_rko_knowledge)


# 9. Выбор расчетного счета (РКО)

@router.message(RegistrationFlow.waiting_for_rko_knowledge, F.text.lower() == "нет")
async def rko_info(message: Message, state: F):
    text = "Что выберете?"
    await message.answer(text, parse_mode="Markdown", reply_markup=kb_banks)
    await state.set_state(RegistrationFlow.waiting_for_rko_choice)


@router.message(RegistrationFlow.waiting_for_rko_knowledge, F.text.lower() == "да")
async def rko_ask(message: Message, state: F):
    await message.answer("Отлично! Выберите банк:", reply_markup=kb_banks)
    await state.set_state(RegistrationFlow.waiting_for_rko_choice)


@router.message(RegistrationFlow.waiting_for_rko_choice)
async def process_rko_choice(message: Message, state: F):
    bank = message.text
    await state.update_data(rko_bank=bank)

    await message.answer(
        f"✅ Принято. Счет будет в: {bank}.\n\n"
        "Следующий вопрос: Сотрудники.\n"
        "Планируете ли вы нанимать людей в штат?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_employees_decision)


# 10. Блок с сотрудниками

@router.message(RegistrationFlow.waiting_for_employees_decision)
async def process_employees(message: Message, state: F):
    decision = message.text
    await state.update_data(need_employees=decision)

    msg = "✅ Понял, работаете в команде." if decision.lower() == "да" else "✅ Понял, работаете самостоятельно."
    await message.answer(
        f"{msg}\n\n"
        "Любой бизнес требует отчетности.\n"
        "Вы знаете, кто будет заниматься вашей бухгалтерией?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_accounting_knowledge)


# 11. Блок бухгалтерии

@router.message(RegistrationFlow.waiting_for_accounting_knowledge, F.text.lower() == "нет")
async def accounting_info(message: Message, state: F):
    text = ("Варианты ведения бухгалтерии:\n"
            "Онлайн\n"
            "Аутсорсинг\n"
            "Штат\n"
            "Приходящий\n\n"
            "Что вам ближе?")
    await message.answer(text, parse_mode="Markdown", reply_markup=kb_accounting_types)
    await state.set_state(RegistrationFlow.waiting_for_accounting_choice)


@router.message(RegistrationFlow.waiting_for_accounting_knowledge, F.text.lower() == "да")
async def accounting_ask(message: Message, state: F):
    await message.answer("Выберите формат бухгалтерии:", reply_markup=kb_accounting_types)
    await state.set_state(RegistrationFlow.waiting_for_accounting_choice)


@router.message(RegistrationFlow.waiting_for_accounting_choice)
async def process_accounting_choice(message: Message, state: F):
    acc_type = message.text
    await state.update_data(accounting_type=acc_type)

    await message.answer(
        f"✅ Принято. Бухгалтерия: {acc_type}.\n\n"
        "Следующий шаг: Помещение.\n"
        "Вы знаете, понадобится ли вам помещение?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_premises_knowledge)


# 12. Блок с определением помещения

@router.message(RegistrationFlow.waiting_for_premises_knowledge, F.text.lower() == "нет")
async def premises_info(message: Message, state: F):
    text = ("Помещение нужно для торговли, общепита или офиса.\n"
        "Для онлайн-бизнеса часто достаточно регистрации по прописке.\n\n"
        "Вам нужно искать коммерческое помещение?")
    await message.answer(text, reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_premises_decision)


@router.message(RegistrationFlow.waiting_for_premises_knowledge, F.text.lower() == "да")
async def premises_ask(message: Message, state: F):
    await message.answer("Нужно ли вам коммерческое помещение?", reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_premises_decision)


@router.message(RegistrationFlow.waiting_for_premises_decision)
async def process_premises_decision(message: Message, state: F):
    decision = message.text
    await state.update_data(need_premises=decision)

    await message.answer(
        "✅ Отлично, идем дальше. CRM-система.\n"
        "Вы знаете, зачем она нужна?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_crm_knowledge)


# 13. Выбор CRM

@router.message(RegistrationFlow.waiting_for_crm_knowledge, F.text.lower() == "нет")
async def crm_info(message: Message, state: F):
    text = ("CRM помогает не терять клиентов.\n"
        "Она напоминает перезвонить, хранит историю заказов и переписок.\n"
        "Без CRM вы будете вести клиентов в блокноте или Excel.\n\n"
        "Вам нужна CRM?")
    await message.answer(text, parse_mode="Markdown", reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_crm_decision)


@router.message(RegistrationFlow.waiting_for_crm_knowledge, F.text.lower() == "да")
async def crm_ask(message: Message, state: F):
    await message.answer("Вам нужна CRM-система?", reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_crm_decision)


@router.message(RegistrationFlow.waiting_for_crm_decision)
async def process_crm_decision(message: Message, state: F):
    decision = message.text
    if decision.lower() == "да":
        await message.answer("Какую CRM выберете?", reply_markup=kb_crm_list)
        await state.set_state(RegistrationFlow.waiting_for_crm_selection)
    else:
        await state.update_data(crm_system="Не нужна")
        await message.answer("✅ Понял. Последний вопрос: Реклама.\nЗнаете, зачем она нужна?",
                             reply_markup=kb_yes_no)
        await state.set_state(RegistrationFlow.waiting_for_ads_knowledge)


@router.message(RegistrationFlow.waiting_for_crm_selection)
async def process_crm_selection(message: Message, state: F):
    crm = message.text
    await state.update_data(crm_system=crm)
    await message.answer(
        f"✅ Отлично, {crm}.\n\n"
        "Последний вопрос: Реклама.\n"
        "Вы знаете, нужна ли вам реклама на старте?",
        reply_markup=kb_yes_no
    )
    await state.set_state(RegistrationFlow.waiting_for_ads_knowledge)


# 14. Блок с рекламой, финальное сообщение для ИП или ООО

@router.message(RegistrationFlow.waiting_for_ads_knowledge, F.text.lower() == "нет")
async def ads_info(message: Message, state: F):
    text = ("Без рекламы о вас узнают только друзья.\n"
            "Для старта можно использовать:\n"
            "— Таргет в соцсетях\n"
            "— Контекстную рекламу (Яндекс)\n"
            "— Гео-сервисы (2ГИС, Карты)\n\n"
            "Планируете запускать рекламу?")
    await message.answer(text, reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_ads_decision)


@router.message(RegistrationFlow.waiting_for_ads_knowledge, F.text.lower() == "да")
async def ads_ask(message: Message, state: F):
    await message.answer("Планируете запускать рекламу?", reply_markup=kb_yes_no)
    await state.set_state(RegistrationFlow.waiting_for_ads_decision)


@router.message(RegistrationFlow.waiting_for_ads_decision)
async def process_final(message: Message, state: F):
    ads_decision = message.text
    await state.update_data(need_ads=ads_decision)

    data = await state.get_data()
    reg_form = data.get('reg_form', 'Неизвестно')
    name = data.get('business_name', 'Мой бизнес')

    # Полный план для ИП / ООО
    final_text = (
        f"План запуска бизнеса: {name}\n\n"
        f"1. Форма: {reg_form}\n"
        f"2. Налоги: {data.get('tax_system', 'УСН')}\n"
        f"3. ОКВЭД: {data.get('okved', '-')}\n"
        f"4. Регистрация: Через {data.get('reg_place')} (Банк: {data.get('reg_bank_name', '-')})\n"
        f"5. Счет (РКО): {data.get('rko_bank', 'Сбер')}\n"
        f"6. Касса: {data.get('kassa_type', '-')}\n"
        f"7. Сотрудники: {data.get('need_employees', 'Нет')}\n"
        f"8. Бухгалтерия: {data.get('accounting_type', '-')}\n"
        f"9. Помещение: {data.get('need_premises', 'Нет')}\n"
        f"10. CRM: {data.get('crm_system', 'Нет')}\n"
        f"11. Реклама: {data.get('need_ads', 'Нет')}\n\n"
        "Следующие шаги:\n"
        "1. Подайте документы на регистрацию.\n"
        "2. После получения документов откройте счет.\n"
        "3. Подключите эквайринг и кассу.\n\n"
        "Успехов в делах!"
    )

    await message.answer(final_text, parse_mode="Markdown")
    await message.answer("Остались ли у вас вопросы?", reply_markup=kb_final)
    await state.set_state(RegistrationFlow.waiting_for_support_question)


# 15. Поддержка и рестарт

@router.message(RegistrationFlow.waiting_for_support_question)
async def support_handler(message: Message, state: F):
    if "Вопросов нет" in message.text:
        await message.answer("Рад был помочь! Если захотите пройти путь заново — жмите /start",
                             reply_markup=kb_restart)
        await state.clear()
    else:
        await message.answer(
            "Номер для консультации: номер.\n"
            "Или напишите в чат поддержки в приложении СберБизнес.",
            reply_markup=kb_restart
        )
        await state.clear()