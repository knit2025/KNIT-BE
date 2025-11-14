from rest_framework import serializers

class CharacterProgressResSerializer(serializers.Serializer):
    familyId = serializers.IntegerField()
    familyCode = serializers.CharField()
    totalPoints = serializers.IntegerField()
    completedItems = serializers.IntegerField()
    currentItem = serializers.CharField(allow_null=True)
    inItemPoints = serializers.IntegerField()
    inItemProgress = serializers.FloatField()
    items = serializers.ListField(child=serializers.CharField())
