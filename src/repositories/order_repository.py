# src/repositories/order_repository.py
from src.repositories.json_repository import JSONRepository
from src.models.order import Order

class OrderRepository:
    FILENAME = "orders.json"

    @classmethod
    def get_all(cls) -> list[Order]:
        data = JSONRepository.load_data(cls.FILENAME)
        return [Order.from_dict(item) for item in data]

    @classmethod
    def get_by_id(cls, order_id: str) -> Order | None:
        orders = cls.get_all()
        for o in orders:
            if o.order_id == order_id:
                return o
        return None

    @classmethod
    def get_by_session(cls, session_id: str) -> list[Order]:
        return [o for o in cls.get_all() if o.session_id == session_id]

    @classmethod
    def save(cls, order: Order) -> bool:
        orders = cls.get_all()
        index = next((i for i, o in enumerate(orders) if o.order_id == order.order_id), -1)
        
        order.compute_total()
        if index >= 0:
            orders[index] = order
        else:
            orders.append(order)
            
        return JSONRepository.save_data(cls.FILENAME, [o.to_dict() for o in orders])

    @classmethod
    def delete(cls, order_id: str) -> bool:
        orders = cls.get_all()
        updated = [o for o in orders if o.order_id != order_id]
        return JSONRepository.save_data(cls.FILENAME, [o.to_dict() for o in updated])