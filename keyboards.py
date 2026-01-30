from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Здесь находятся утилиты и общие кнопки

def kb_nav(rows: list[list[KeyboardButton]]):

    # Нижний ряд кнопок для навигации в режиме опроса
    rows.append([
        KeyboardButton(text="Назад"),
        KeyboardButton(text="В главное меню")
    ])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

# Кнопки главного меню
kb_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Составить бизнес-план")],
        [KeyboardButton(text="Спросить у GigaChat")]
    ],
    resize_keyboard=True
)

# Клавитура чата с ИИ
kb_ai_chat = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Контакты поддержки"), KeyboardButton(text="В главное меню")]
    ],
    resize_keyboard=True
)

# Кнопка возврата в меню для первого шага в опросе, где нет "Назад"
kb_back_to_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="В главное меню")]],
    resize_keyboard=True
)

# Финальные кнопки опроса. Без кнопки "Назад", только Меню и Поддержка
kb_final = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вопросов нет, спасибо!")],
        [KeyboardButton(text="Остались вопросы")],
        [KeyboardButton(text="В главное меню")]
    ],
    resize_keyboard=True
)

# Кнопка возврата в главное меню. Перезапуск бота
kb_restart = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="В главное меню")]],
    resize_keyboard=True
)

# Общие кнопки опросника

# Выбор банков (Блоки: 1.1, 1.2, 4, 5, 6, 7)
kb_banks = kb_nav([
    [KeyboardButton(text="СберБанк"), KeyboardButton(text="Альфа")],
    [KeyboardButton(text="ВТБ"), KeyboardButton(text="Другой")],
    [KeyboardButton(text="Как выбрать банк? (PDF)")]
])

# Кнопки "Да"/"Нет" в один ряд, универсально и опционально (Блоки: 7, 8, 9)
kb_yes_no = kb_nav([
    [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
])

# Этапы опросника

# Форма регистрации (Блок 1.1, 1.2, 2)
kb_form_types = kb_nav([
    [KeyboardButton(text="Самозанятый"), KeyboardButton(text="ИП")],
    [KeyboardButton(text="ООО"), KeyboardButton(text="Помогите выбрать (PDF)")]
])

# Налоги (Блоки: 1.1, 2, 3)
kb_tax_regimes = kb_nav([
    [KeyboardButton(text="УСН (Доходы)"), KeyboardButton(text="УСН (Доходы-Расходы)")],
    [KeyboardButton(text="Патент"), KeyboardButton(text="ОСНО")],
    [KeyboardButton(text="АУСН"), KeyboardButton(text="Какую систему выбрать? (PDF)")]
])

# ОКВЭД (Блоки: 3, 4)
kb_okved_top = kb_nav([
    [KeyboardButton(text="IT и разработка"), KeyboardButton(text="Розничная торговля")],
    [KeyboardButton(text="Кафе / Общепит"), KeyboardButton(text="Строительство")],
    [KeyboardButton(text="Салон красоты"), KeyboardButton(text="Грузоперевозки")],
    [KeyboardButton(text="Ввести код вручную"), KeyboardButton(text="Что такое ОКВЭД? (PDF)")]
])

# Вспомогательная клавиатура для шагов ручного ввода ОКВЭД
# (Только навигация) (Блок 3)
kb_input_nav = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад"), KeyboardButton(text="В главное меню")]
    ],
    resize_keyboard=True
)

# Места регистрации (Блоки: 3, 4, 5)
kb_reg_places = kb_nav([
    [KeyboardButton(text="Через Банк (Онлайн)"), KeyboardButton(text="Госуслуги")],
    [KeyboardButton(text="МФЦ / ФНС"), KeyboardButton(text="Где лучше зарегистрировать? (PDF)")],
])

# Нужен ли эквайринг (Блоки: 5, 6, 7)
kb_acquiring_decision = kb_nav([
    [KeyboardButton(text="Да, нужно"), KeyboardButton(text="Нет, не нужно")],
    [KeyboardButton(text="Что такое эквайринг? (PDF)")]
])

# Кассы (Блоки: 4, 5, 6)
kb_kassa_types = kb_nav([
    [KeyboardButton(text="Офлайн касса"), KeyboardButton(text="Онлайн касса")],
    [KeyboardButton(text="Гибрид (Оба варианта)"), KeyboardButton(text="Нужна помощь с кассой (PDF)")],
])

# Бухгалтерия (Блоки: 8, 9, 10)
kb_accounting_types = kb_nav([
    [KeyboardButton(text="Онлайн-бухгалтерия"), KeyboardButton(text="Аутсорсинг")],
    [KeyboardButton(text="Штатный бухгалтер"), KeyboardButton(text="Приходящий бухгалтер")],
    [KeyboardButton(text="Как вести бухгалтерию? (PDF)")]
])

# Помещение (Блоки: 9, 10, 11)
kb_premises = kb_nav([
    [KeyboardButton(text="Да, нужно"), KeyboardButton(text="Нет, не нужно")],
    [KeyboardButton(text="Зачем нужно помещение? (PDF)")]
])

# CRM (Решение) (Блоки: 10, 11, 12)
kb_crm_decision = kb_nav([
    [KeyboardButton(text="Выбрать CRM"), KeyboardButton(text="Не нужна")],
    [KeyboardButton(text="Что такое CRM? (PDF)")]
])

# CRM (Список) (Блок 11)
kb_crm_list = kb_nav([
    [KeyboardButton(text="SberCRM")],
    [KeyboardButton(text="AmoCRM"), KeyboardButton(text="Битрикс24")]
])

# Реклама (Блоки: 11, 12)
kb_ads = kb_nav([
    [KeyboardButton(text="Да, планирую"), KeyboardButton(text="Нет, не планирую")],
    [KeyboardButton(text="Зачем нужна реклама? (PDF)")]
])