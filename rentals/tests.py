import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rentals.models import Car, Rental
from decimal import Decimal

class CarAPITestCase(TestCase):
    """Casos de teste para API de Carros"""
    
    def setUp(self):
        self.client = APIClient()
        self.car = Car.objects.create(
            brand="Toyota",
            model="Corolla",
            year=2020,
            daily_rate=Decimal("50.00"),
            available=True
        )
    
    def test_deve_obter_carros_disponiveis(self):
        """Teste para obter carros disponíveis"""
        response = self.client.get('/api/cars/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cars', response.data)
        self.assertEqual(len(response.data['cars']), 1)
    
    def test_deve_obter_carro_por_id(self):
        response = self.client.get(f'/api/cars/{self.car.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['brand'], 'Toyota')

class RentalAPITestCase(TestCase):
    """Casos de teste para API de Locação de Carros"""
    
    def setUp(self):
        self.client = APIClient()
        self.car = Car.objects.create(
            brand="Honda",
            model="Civic",
            year=2021,
            daily_rate=Decimal("55.00"),
            available=True
        )
    
    def test_deve_criar_locacao(self):
        """Teste para criar uma locação válida"""
        data = {
            "car_id": self.car.id,
            "customer_name": "João Silva",
            "customer_email": "joao@example.com",
            "days": 5
        }
        
        response = self.client.post('/api/rentals/create', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Rental.objects.count(), 1)
        
        self.car.refresh_from_db()
        self.assertFalse(self.car.available)