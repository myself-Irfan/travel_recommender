from django.test import TestCase

from travel.serializers.best_districts_serializer import BestDistrictsSerializer


class BestDistrictsSerializerTest(TestCase):
    def test_valid_limit(self):
        """Test valid limit values"""
        serializer = BestDistrictsSerializer(data={"limit": 5})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["limit"], 5)

    def test_default_limit(self):
        """Test default limit when not provided"""
        serializer = BestDistrictsSerializer(data={})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["limit"], 10)

    def test_limit_too_low(self):
        """Test limit below minimum"""
        serializer = BestDistrictsSerializer(data={"limit": 0})
        self.assertFalse(serializer.is_valid())

    def test_limit_too_high(self):
        """Test limit above maximum"""
        serializer = BestDistrictsSerializer(data={"limit": 100})
        self.assertFalse(serializer.is_valid())