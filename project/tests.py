from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Type, Content
from .serializers import TypeSerializer, ContentSerializer
import json

# ==================== МОДЕЛЬНЫЕ ТЕСТЫ ====================
class TypeModelTest(TestCase):
    def setUp(self):
        self.type = Type.objects.create(name="Тестовый тип")
    
    def test_type_creation(self):
        """Тест создания объекта Type"""
        self.assertEqual(self.type.name, "Тестовый тип")
        self.assertEqual(str(self.type), "Тестовый тип")
    
    def test_type_str_method(self):
        """Тест строкового представления Type"""
        self.assertEqual(str(self.type), self.type.name)


class ContentModelTest(TestCase):
    def setUp(self):
        self.type = Type.objects.create(name="Тип для контента")
        self.content = Content.objects.create(
            name="Тестовый контент",
            type=self.type
        )
    
    def test_content_creation(self):
        """Тест создания объекта Content"""
        self.assertEqual(self.content.name, "Тестовый контент")
        self.assertEqual(self.content.type, self.type)
    
    def test_content_without_type(self):
        """Тест создания Content без типа (должно быть null=True)"""
        content = Content.objects.create(name="Контент без типа")
        self.assertIsNone(content.type)


# ==================== СЕРИАЛИЗАТОРЫ ТЕСТЫ ====================
class TypeSerializerTest(TestCase):
    def setUp(self):
        self.type_data = {'name': 'Новый тип'}
        self.serializer = TypeSerializer(data=self.type_data)
    
    def test_type_serializer_valid(self):
        """Тест валидности сериализатора Type"""
        self.assertTrue(self.serializer.is_valid())
        self.assertEqual(self.serializer.validated_data['name'], 'Новый тип')
    
    def test_type_serializer_invalid(self):
        """Тест невалидных данных сериализатора Type"""
        invalid_data = {'name': ''}
        serializer = TypeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class ContentSerializerTest(TestCase):
    def setUp(self):
        self.type = Type.objects.create(name='Тип для сериализатора')
        self.content_data = {
            'name': 'Контент для сериализатора',
            'type_id': self.type.id
        }
        self.serializer = ContentSerializer(data=self.content_data)
    
    def test_content_serializer_valid(self):
        """Тест валидности сериализатора Content"""
        self.assertTrue(self.serializer.is_valid())
    
    def test_content_serializer_read(self):
        """Тест чтения данных из Content сериализатора"""
        content = Content.objects.create(
            name='Тестовый контент',
            type=self.type
        )
        serializer = ContentSerializer(content)
        data = serializer.data
        self.assertEqual(data['name'], 'Тестовый контент')
        self.assertEqual(data['type']['name'], 'Тип для сериализатора')


# ==================== API ТЕСТЫ ====================
class TypeAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.type = Type.objects.create(name='Тип API')
        self.list_url = '/api/types/'  # Предполагаемый URL
        self.detail_url = f'/api/types/{self.type.id}/'
    
    def test_get_type_list(self):
        """Тест получения списка типов через API"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_type(self):
        """Тест создания типа через API"""
        data = {'name': 'Созданный через API'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Type.objects.count(), 2)
    
    def test_get_type_detail(self):
        """Тест получения деталей типа"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.type.name)
    
    def test_update_type(self):
        """Тест обновления типа"""
        data = {'name': 'Обновленный тип'}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.type.refresh_from_db()
        self.assertEqual(self.type.name, 'Обновленный тип')
    
    def test_delete_type(self):
        """Тест удаления типа"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Type.objects.count(), 0)


class ContentAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.type = Type.objects.create(name='Тип для контента API')
        self.content = Content.objects.create(
            name='Контент API',
            type=self.type
        )
        self.list_url = '/api/contents/'  # Предполагаемый URL
        self.detail_url = f'/api/contents/{self.content.id}/'
    
    def test_get_content_list(self):
        """Тест получения списка контента"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_content(self):
        """Тест создания контента"""
        data = {
            'name': 'Новый контент',
            'type_id': self.type.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Content.objects.count(), 2)
    
    def test_create_content_without_type(self):
        """Тест создания контента без типа"""
        data = {'name': 'Контент без типа'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_content_detail(self):
        """Тест получения деталей контента"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Контент API')
    
    def test_update_content(self):
        """Тест обновления контента"""
        new_type = Type.objects.create(name='Новый тип для обновления')
        data = {
            'name': 'Обновленный контент',
            'type_id': new_type.id
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.content.refresh_from_db()
        self.assertEqual(self.content.name, 'Обновленный контент')
        self.assertEqual(self.content.type, new_type)
    
    def test_delete_content(self):
        """Тест удаления контента"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Content.objects.count(), 0)


# ==================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ====================
class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.type = Type.objects.create(name='Интеграционный тип')
        self.content = Content.objects.create(
            name='Интеграционный контент',
            type=self.type
        )
    
    def test_type_content_relationship(self):
        """Тест связи между Type и Content"""
        content = Content.objects.get(id=self.content.id)
        self.assertEqual(content.type.name, 'Интеграционный тип')
        
        # Проверяем обратную связь
        type_obj = Type.objects.get(id=self.type.id)
        contents = type_obj.content_set.all()
        self.assertIn(self.content, contents)
    
    def test_cascade_delete(self):
        """Тест каскадного удаления"""
        # При удалении Type должны удаляться связанные Content
        type_count = Type.objects.count()
        content_count = Content.objects.count()
        
        self.type.delete()
        
        self.assertEqual(Type.objects.count(), type_count - 1)
        self.assertEqual(Content.objects.count(), content_count - 1)




# ==================== ТЕСТЫ ДЛЯ РАБОТЫ С JSON ====================
class JSONResponseTests(APITestCase):
    def setUp(self):
        self.type = Type.objects.create(name='Тип для JSON')
        self.content = Content.objects.create(
            name='Контент для JSON',
            type=self.type
        )
        self.client = APIClient()
    
    def test_json_structure_type(self):
        """Тест структуры JSON для Type"""
        response = self.client.get(f'/api/types/{self.type.id}/')
        data = response.json()
        
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Тип для JSON')
    


# ==================== ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ ====================
class PerformanceTests(TestCase):
    def test_bulk_create_types(self):
        """Тест массового создания типов"""
        types_to_create = [
            Type(name=f'Тип {i}')
            for i in range(100)
        ]
        Type.objects.bulk_create(types_to_create)
        self.assertEqual(Type.objects.count(), 100)
    
    def test_bulk_create_contents(self):
        """Тест массового создания контента"""
        type_obj = Type.objects.create(name='Массовый тип')
        
        contents_to_create = [
            Content(name=f'Контент {i}', type=type_obj)
            for i in range(50)
        ]
        Content.objects.bulk_create(contents_to_create)
        self.assertEqual(Content.objects.count(), 50)


if __name__ == '__main__':
    import unittest
    unittest.main()