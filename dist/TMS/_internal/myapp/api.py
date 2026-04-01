from rest_framework import serializers, viewsets
from .models import Tricycle

class TricycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tricycle
        fields = '__all__'

class TricycleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tricycle.objects.all()
    serializer_class =TricycleSerializer

