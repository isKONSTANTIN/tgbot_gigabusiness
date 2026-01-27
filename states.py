from aiogram.fsm.state import StatesGroup, State


class RegistrationFlow(StatesGroup):
    # Знакомство
    waiting_for_start_decision = State()         # Хочет ли человек открыть бизнес?
    waiting_for_business_name = State()          # Название компании
    waiting_for_form_knowledge = State()         # Знаете ли какая форма регистрации нужна?
    waiting_for_form_choice = State()            # Выбор формы регистрации

    # Ветка ИП/ООО (Налоги)
    waiting_for_tax_knowledge = State()           # Знаете ли вы налоговый режим?
    waiting_for_tax_choice = State()              # Выбор режима

    # Ветка самозанятый (Счет)
    waiting_for_account_existence = State()       # Есть ли счет?
    waiting_for_bank_choice = State()             # Выбор банка

    # ОКВЭД
    waiting_for_okved_knowledge = State()         # Знаете ли код?
    waiting_for_okved_selection = State()         # Выбор конкретного кода

    # Место регистрации
    waiting_for_reg_place_knowledge = State()     # Знаете где?
    waiting_for_reg_place_choice = State()        # Выбор (Банк/МФЦ/Госуслуги)

    # Доп. ветка, если выбрали банк
    waiting_for_reg_bank_knowledge = State()      # Знаете какой банк?
    waiting_for_reg_bank_choice = State()         # Выбор конкретного банка

    # Касса
    waiting_for_kassa_knowledge = State()         # Знаете какая касса нужна?
    waiting_for_kassa_choice = State()            # Выбор кассы

    # Расчетный счет (РКО)
    waiting_for_rko_knowledge = State()           # Знаете где открывать?
    waiting_for_rko_choice = State()              # Выбор банка

    # Сотрудники
    waiting_for_employees_decision = State()      # Нужны ли сотрудники?

    # Бухгалтерия
    waiting_for_accounting_knowledge = State()    # Знаете кто будет вести?
    waiting_for_accounting_choice = State()       # Выбор типа бухгалтерии

    # Помещение
    waiting_for_premises_knowledge = State()      # Знаете зачем?
    waiting_for_premises_decision = State()       # Нужно ли помещение?

    # CRM система
    waiting_for_crm_knowledge = State()           # Знаете зачем?
    waiting_for_crm_decision = State()            # Нужна ли CRM?
    waiting_for_crm_selection = State()           # Выбор конкретной CRM

    # Реклама
    waiting_for_ads_knowledge = State()           # Знаете зачем?
    waiting_for_ads_decision = State()            # Нужна ли реклама?

    # Финал
    waiting_for_support_question = State()        # Остались вопросы?