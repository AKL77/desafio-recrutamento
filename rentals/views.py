from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Car, Rental
from .serializers import CarSerializer, RentalSerializer, RentalCreateSerializer
from . import database
from . import utils
from . import services

@api_view(['GET'])
def index(request):
    """Endpoint de boas-vindas"""
    return Response({"message": "Welcome to Car Rental API"})


@api_view(['GET'])
def get_cars(request):
    cars = database.get_available_cars()
    serializer = CarSerializer(cars, many=True)
    return Response({"cars": serializer.data})


@api_view(['GET'])
def get_car(request, car_id):
    car = database.get_car_by_id(car_id)
    if car is None:
        return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CarSerializer(car)
    return Response(serializer.data)


@api_view(['POST'])
def create_rental(request):
    serializer = RentalCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data

    try:
        rental = services.process_new_rental(
            car_id=data['car_id'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            days=data['days']
        )
        return Response(RentalSerializer(rental).data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        erro = str(e)
        if erro == "Car not found":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return Response({"error": erro}, status=status_code)


@api_view(['POST'])
def return_rental(request, rental_id):
    try:
        rental = services.process_return_rental(rental_id)
        return Response({
            "message": "Car returned successfully",
            "rental": RentalSerializer(rental).data
        })
    except ValueError as e:
        erro = str(e)
        if erro == "Rental not found":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return Response({"error": erro}, status=status_code)


@api_view(['GET'])
def get_rentals(request):
    rentals = database.get_all_rentals()
    serializer = RentalSerializer(rentals, many=True)
    return Response({"rentals": serializer.data})


@api_view(['GET'])
def get_customer_rentals(request, customer_email):
    """Obter locações para um cliente específico"""
    rentals = database.get_customer_rentals(customer_email)
    serializer = RentalSerializer(rentals, many=True)
    return Response({"rentals": serializer.data})


@api_view(['GET'])
def get_stats(request):
    stats = database.get_rental_stats()
    return Response(stats)

