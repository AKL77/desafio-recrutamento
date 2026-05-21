import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rentals.models import Car, Rental
from decimal import Decimal

from django.utils import timezone
from datetime import timedelta

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

    def test_desconto_sete_dias(self):
        data = {
            "car_id": self.car.id,
            "customer_name": "Maria Oliveira",
            "customer_email": "maria@example.com",
            "days": 10
        }
        
        response = self.client.post('/api/rentals/create', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_devolver_carro_com_atraso(self):
        """Teste para devolver um carro com atraso e calcular multa"""
        rental = Rental.objects.create(
            car=self.car,
            customer_name="Augusto Lunardi",
            customer_email="augusto@example.com",
            start_date = timezone.now() - timedelta(days=10),
            end_date = timezone.now() - timedelta(days=5),
            total_cost = Decimal("275.00"),
            returned=False
        )

        response = self.client.post(f'/api/rentals/{rental.id}/return/', format = 'json')
        self.assertEqual(response.status_code, 200)

        self.car.refresh_from_db()
        self.assertTrue(self.car.available)

        rental.refresh_from_db()
        self.assertTrue(rental.returned)
        self.assertIsNotNone(rental.late_fee)

    def test_alugar_carro_indisponivel(self):
        """Teste para tentar alugar um carro que já está alugado"""
        self.car.available = False
        self.car.save()

        data = {
            "car_id": self.car.id,
            "customer_name": "Samuel Samuel",
            "customer_email": "samuel@example.com",
            "days": 3
        }

        response = self.client.post('/api/rentals/create', data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_devolver_carro_ja_devolvido(self):
        """Teste para tentar devolver um carro que já foi devolvido"""
        rental = Rental.objects.create(
            car=self.car,
            customer_name="Lucas Silva",
            customer_email="lucas@example.com",
            start_date=timezone.now() - timedelta(days=5),
            end_date=timezone.now(),
            total_cost=Decimal("250.00"),
            returned=True
        )

        response = self.client.post(f'/api/rentals/{rental.id}/return/', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_devolver_carro_nao_encontrado(self):
        """Teste para tentar devolver um carro com ID de locação inválido"""
        response = self.client.post('/api/rentals/999/return/', format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
