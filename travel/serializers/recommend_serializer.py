from rest_framework import serializers
from datetime import date


class RecommendSerializer(serializers.Serializer):
    current_lat = serializers.FloatField(min_value=-90, max_value=90)
    current_lon = serializers.FloatField(min_value=-180, max_value=180)
    destination_name = serializers.CharField(max_length=255, trim_whitespace=True)
    travel_date = serializers.DateField()

    def validate_travel_date(self, value):
        from datetime import timedelta
        today = date.today()
        max_date = today + timedelta(days=7)

        if value < today:
            raise serializers.ValidationError("Travel date cannot be in the past.")
        if value > max_date:
            raise serializers.ValidationError("Travel date must be within the next 7 days.")

        return value