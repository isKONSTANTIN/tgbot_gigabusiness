from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура Да/Нет
kb_yes_no = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавиатура выбора формы
kb_form_types = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Самозанятый")],
        [KeyboardButton(text="ИП"), KeyboardButton(text="ООО")],
        [KeyboardButton(text="Помогите выбрать")] ### Заглушено
    ],
    resize_keyboard=True
)

# Кнопка отмены/назад (Пока не реализовано)
kb_cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="В главное меню")]],
    resize_keyboard=True
)

# Выбор налогового режима
kb_tax_regimes = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="УСН (Доходы)"), KeyboardButton(text="УСН (Доходы-Расходы)")],
        [KeyboardButton(text="Патент (ПСН)"), KeyboardButton(text="ОСНО")],
        [KeyboardButton(text="АУСН (Автоматика)")],
    ],
    resize_keyboard=True
)

# Выбор банка
kb_banks = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="СберБанк")],
        [KeyboardButton(text="Альфа"), KeyboardButton(text="ВТБ")],
        [KeyboardButton(text="Другой")]
    ],
    resize_keyboard=True
)

# Клавиатура популярных ОКВЭД
kb_okved_top = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="IT и разработка"), KeyboardButton(text="Розничная торговля")],
        [KeyboardButton(text="Кафе / Общепит"), KeyboardButton(text="Строительство / Ремонт")],
        [KeyboardButton(text="Салон красоты"), KeyboardButton(text="Грузоперевозки")],
        [KeyboardButton(text="Ввести свой код вручную")]
    ],
    resize_keyboard=True
)

# Клавиатура мест регистрации
kb_reg_places = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Банк")],
        [KeyboardButton(text="Госуслуги"), KeyboardButton(text="МФЦ")]
    ],
    resize_keyboard=True
)

# Клавиатура типов касс
kb_kassa_types = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Офлайн касса (Торговая точка)")],
        [KeyboardButton(text="Онлайн касса (Интернет)")],
        [KeyboardButton(text="Гибрид (Офлайн + Онлайн)")]
    ],
    resize_keyboard=True
)

# Клавиатура типов бухгалтерии
kb_accounting_types = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Онлайн-бухгалтерия (Банк)")],
        [KeyboardButton(text="Аутсорсинг (Фирма)")],
        [KeyboardButton(text="Штатный бухгалтер"), KeyboardButton(text="Приходящий бухгалтер")]
    ],
    resize_keyboard=True
)

# Клавиатура со списком CRM
kb_crm_list = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="SberCRM")],
        [KeyboardButton(text="AmoCRM"), KeyboardButton(text="Битрикс24")]
    ],
    resize_keyboard=True
)

# Финальная клавиатура
kb_final = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вопросов нет, спасибо!")],
        [KeyboardButton(text="Есть вопрос (в поддержку)")]
    ],
    resize_keyboard=True
)

# Клавиатура с перезапуском
kb_restart = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start")]],
    resize_keyboard=True
)