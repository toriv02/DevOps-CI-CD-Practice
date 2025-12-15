from rest_framework import serializers

from project.models import *

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = "__all__"

class ContentSerializer(serializers.ModelSerializer):
    type=TypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=Type.objects.all(), 
        source='type', 
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Content
        fields = "__all__"