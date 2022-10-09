from rest_framework import serializers


class RoleSerializer(serializers.Serializer):
    role=serializers.CharField(required=True)
