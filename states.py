from aiogram.fsm.state import StatesGroup, State


class RegistrationFlow(StatesGroup):

    # Режим чата с ИИ
    ai_chat_mode = State()

    # Опросник
    waiting_for_business_name = State()      # Название компании
    waiting_for_form_choice = State()        # Сразу выбор формы

    # Ветка ИП/ООО (Налоги)
    waiting_for_tax_choice = State()         # Сразу выбор налога

    # Ветка самозанятый (Счет)
    waiting_for_bank_choice_self = State()   # Выбор банка (самозанятый)

    # ОКВЭД
    waiting_for_okved_selection = State()    # Выбор из меню
    waiting_for_okved_custom = State()       # НОВОЕ: Ручной ввод ОКВЭД

    # Место регистрации
    waiting_for_reg_place_choice = State()   # Выбор места

    # Банк для регистрации (подветка)
    waiting_for_reg_bank_choice = State()

    # Касса
    waiting_for_kassa_choice = State()

    # Эквайринг
    waiting_for_acquiring_decision = State() # Да/Нет
    waiting_for_acquiring_bank = State()     # Выбор банка

    # Расчетный счет (РКО)
    waiting_for_rko_choice = State()

    # Сотрудники
    waiting_for_employees_decision = State()

    # Бухгалтерия
    waiting_for_accounting_choice = State()

    # Помещение
    waiting_for_premises_decision = State()

    # CRM
    waiting_for_crm_decision = State()
    waiting_for_crm_selection = State()

    # Реклама
    waiting_for_ads_decision = State()

    # Финал (после опроса)
    waiting_for_support_question = State()