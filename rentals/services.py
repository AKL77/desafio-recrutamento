from django.utils import timezone
from datetime import timedelta
from . import database, utils

def process_new_rental(car_id, customer_name, customer_email, days):
    car = database.get_car_by_id(car_id)
    if car is None:
        raise ValueError("Car not found")
    
    if not car.available:
        raise ValueError("Car is not available for rental")
        
    start_date = timezone.now()
    end_date = start_date + timedelta(days=days)
    
    total_cost = car.daily_rate * days
    discount = utils.calculate_discount(days, total_cost)
    total_cost = total_cost - discount
    
    rental = database.create_rental(
        car_id=car.id,
        customer_name=customer_name,
        customer_email=customer_email,
        start_date=start_date,
        end_date=end_date,
        total_cost=total_cost
    )
    
    car.available = False
    database.update_car(car)
    
    return rental

def process_return_rental(rental_id):
    rental = database.get_rental_by_id(rental_id)
    if rental is None:
        raise ValueError("Rental not found")
        
    if rental.returned:
        raise ValueError("Car already returned")
        
    rental.returned = True
    rental.actual_return_date = timezone.now()
    
    if rental.actual_return_date > rental.end_date:
        late_days = (rental.actual_return_date - rental.end_date).days
        rental.late_fee = utils.calculate_late_fee(late_days, rental.car.daily_rate)
        rental.total_cost = rental.total_cost + rental.late_fee
        
    database.update_rental(rental)
    
    car = rental.car
    car.available = True
    database.update_car(car)
    
    return rental