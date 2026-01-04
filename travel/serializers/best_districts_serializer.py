from rest_framework import serializers


class BestDistrictsSerializer(serializers.Serializer):
    limit = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=64,
        required=False,
        help_text="Number of top districts to return"
    )