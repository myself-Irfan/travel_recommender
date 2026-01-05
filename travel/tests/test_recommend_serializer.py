from django.test import TestCase
from datetime import date, timedelta

from travel.serializers.recommend_serializer import RecommendSerializer


class RecommendSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "current_lat": 23.8103,
            "current_lon": 90.4125,
            "destination_name": "Sylhet",
            "travel_date": (date.today() + timedelta(days=3)).isoformat()
        }

    def test_valid_data(self):
        """Test valid recommendation data"""
        serializer = RecommendSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_missing_required_fields(self):
        """Test missing required fields"""
        serializer = RecommendSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("current_lat", serializer.errors)
        self.assertIn("current_lon", serializer.errors)
        self.assertIn("destination_name", serializer.errors)
        self.assertIn("travel_date", serializer.errors)

    def test_invalid_latitude(self):
        """Test invalid latitude"""
        data = self.valid_data.copy()
        data["current_lat"] = 100
        serializer = RecommendSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_longitude(self):
        """Test invalid longitude"""
        data = self.valid_data.copy()
        data["current_lon"] = -200
        serializer = RecommendSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_travel_date_in_past(self):
        """Test travel date validation - past date"""
        data = self.valid_data.copy()
        data["travel_date"] = (date.today() - timedelta(days=1)).isoformat()
        serializer = RecommendSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("travel_date", serializer.errors)

    def test_travel_date_too_far(self):
        data = self.valid_data.copy()
        data["travel_date"] = (date.today() + timedelta(days=10)).isoformat()
        serializer = RecommendSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("travel_date", serializer.errors)

    def test_whitespace_trimming(self):
        data = self.valid_data.copy()
        data["destination_name"] = "  Sylhet  "
        serializer = RecommendSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["destination_name"], "Sylhet")