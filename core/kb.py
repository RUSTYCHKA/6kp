from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pandas as pd

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Запустить", callback_data="start")],
    ]
)

start_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Начать рассылку", callback_data="start_message")],
    ]
)

new_message = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Новая рассылка",
                              callback_data="start")],
    ]
)

res_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Результаты", switch_inline_query_current_chat="results")],
    ]
)


def get_categories_button():
    keyboard = []
    
    data = pd.ExcelFile("sites_data.xlsx")

    
    
    for sheet in data.sheet_names:
        keyboard.append([InlineKeyboardButton(text=sheet, callback_data=f"category={sheet}")])
    keyboard.append([InlineKeyboardButton(
        text="Все", callback_data="category=all")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

