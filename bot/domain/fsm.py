from aiogram.fsm.state import State, StatesGroup


class Order(StatesGroup):
    """FSM состояния для процесса заказа пиццы."""

    wait_for_pizza_name = State()
    wait_for_pizza_size = State()
    wait_for_drinks = State()
    wait_for_order_approve = State()
    wait_for_payment = State()
    order_finished = State()
