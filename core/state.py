from aiogram.fsm.state import StatesGroup, State



class UserStates(StatesGroup):
    MAIN = State()
    ADMIN = State()
    waiting_for_password = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()