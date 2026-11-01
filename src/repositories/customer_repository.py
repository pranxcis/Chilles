# src/repositories/customer_repository.py
from src.repositories.json_repository import JSONRepository
from src.models.customer import Customer

class CustomerRepository:
    FILENAME = "customers.json"

    @classmethod
    def get_all(cls) -> list[Customer]:
        data = JSONRepository.load_data(cls.FILENAME)
        return [Customer.from_dict(item) for item in data]

    @classmethod
    def get_by_id(cls, customer_id: str) -> Customer | None:
        customers = cls.get_all()
        for c in customers:
            if c.customer_id == customer_id:
                return c
        return None

    @classmethod
    def get_by_phone(cls, phone: str) -> Customer | None:
        customers = cls.get_all()
        clean_phone = phone.strip()
        for c in customers:
            if c.phone.strip() == clean_phone:
                return c
        return None

    @classmethod
    def save(cls, customer: Customer) -> bool:
        customers = cls.get_all()
        index = next((i for i, c in enumerate(customers) if c.customer_id == customer.customer_id), -1)
        
        if index >= 0:
            customers[index] = customer
        else:
            customers.append(customer)
            
        return JSONRepository.save_data(cls.FILENAME, [c.to_dict() for c in customers])

    @classmethod
    def delete(cls, customer_id: str) -> bool:
        customers = cls.get_all()
        updated = [c for c in customers if c.customer_id != customer_id]
        return JSONRepository.save_data(cls.FILENAME, [c.to_dict() for c in updated])