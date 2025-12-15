from rest_framework import serializers


class IndexQueryDataSerializer(serializers.Serializer):
    """Serializer for index query data"""
    index_id = serializers.IntegerField()
    cardinality = serializers.IntegerField()
    rows_count = serializers.IntegerField()
    date_query = serializers.CharField(required=False, allow_blank=True)
    received_rows_id = serializers.IntegerField(required=False, allow_null=True)


class CalculationRequestSerializer(serializers.Serializer):
    """Serializer for calculation request"""
    query_id = serializers.IntegerField()
    indexes_data = IndexQueryDataSerializer(many=True)
