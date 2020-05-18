from decimal import Decimal
from django.conf import settings
from .models import Item
from django.contrib.sessions.models import Session


def user_sessions(user_id):
    """
    Находит все сессии пользователя
    :param user_id: str
    :return: list of user_sessions
    """
    sessions = Session.objects.all()
    result = []
    for i in range(len(sessions)):
        if sessions[i].get_decoded()['_auth_user_id'] == user_id:
            result.append(sessions[i])
    return result


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        # print(request.session.items())
        user_id = request.session.get('_auth_user_id')
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            print(f'Тележка пуста {cart}')
            cart = self.session[settings.CART_SESSION_ID] = {}
            sessions = Session.objects.all()
            for i in range(len(sessions)):
                data_other_session = sessions[i].get_decoded()
                # Ищем сессию этого же пользователя с заполненной корзиной
                if data_other_session['_auth_user_id'] == user_id and \
                        'cart' in data_other_session and \
                        data_other_session['cart']:
                    cart = data_other_session['cart']
                    # sessions[i].delete() # Скопировали корзину и удаляем предыдущую сессию
                    break
        # print(cart)
        self.cart = cart
        # self.save()

    def add(self, item, quantity: int = 1, update_quantity: bool = False):
        """
        Добавление товара в корзину
        add(item, quantity, update_quantity)
        item - модель из бд
        quantity - (int) количество заказа (default 1
        update_quantity - (boolean)- Обновление количества (default False)
        """
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0}
            # self.cart[item_id] = 0
        print(f"{update_quantity=}")
        if update_quantity:
            print("ЗАМЕНЯЮ")
            self.cart[item_id]['quantity'] = quantity
        else:
            print("ПЛЮСУЮ")
            self.cart[item_id]['quantity'] += quantity
        print(self.cart)
        self.save()

    def save(self):  # Сохраннение корзины в сессии
        """
        Сохранение корзины в сессиии
        :return:
        """
        for item in self.cart:
            # Перед сохранение удаляем не сериализируемые обьекты
            if "item" in self.cart[item]:
                del self.cart[item]["item"]
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, item):  # Удаление из корзины
        """
        Удаление элемента из корзины
        :param item: Item model
        :return:
        """
        item_id = str(item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def __iter__(self):  # Итератор
        """

        :return: иетратор по товарам в корзине
        """
        item_ids = self.cart.keys()
        items = Item.objects.filter(id__in=item_ids)
        cart = self.cart.copy()
        for item in items:
            cart[str(item.id)]['item'] = item

        for item in cart.values():
            yield item

    def __len__(self):  # TODO нужно переделать под различные виды (весовые штучные)
        return sum(val['quantity'] for val in self.cart.values())

    def count_items(self, item_id=False):  # Количество позиций в корзине
        if item_id:
            count = int(self.cart[str(item_id)]['quantity'])
            return count
        else:
            return len(self.cart)

    def clear(self):
        """
        Чистит корзину пользователя
        И удаляет другие сесии пользотваеля,
        что бы оттуда корзина не скопировалась
        :return: None
        """
        sessions = user_sessions(self.session.get('_auth_user_id'))
        print(self.session.session_key)
        for session in sessions:
            if session.session_key != self.session.session_key:
                session.delete()
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def __contains__(self, item):
        item_ids = self.cart.keys()
        return item in item_ids

