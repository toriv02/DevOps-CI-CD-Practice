from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets

from project.models import *
from project.serializers import *

class ContentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
    ):
    queryset=Content.objects.all()
    serializer_class=ContentSerializer

class TypeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset=Type.objects.all()
    serializer_class=TypeSerializer