# Copyright 2022, themeontology.org
# Tests:
from rest_framework import serializers
from .models import Theme, Story, StoryTheme


class TOTOLOSerializer(serializers.ModelSerializer):
    weight = serializers.SerializerMethodField()

    def __init__(self, *args, weight_index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._weight_index = weight_index

    def get_weight(self, instance):
        if self._weight_index and instance:
            return self._weight_index[instance.idx]
        return 0


class StorySerializer(TOTOLOSerializer):
    class Meta:
        model = Story
        fields = (
            'sid', 'title', 'date', 'parents', 'children', 'description', 'source', 'ratings', 'weight',
        )


class ThemeSerializer(TOTOLOSerializer):
    class Meta:
        model = Theme
        fields = (
            'name', 'parents', 'children', 'description', 'source', 'weight',
        )


class StoryThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryTheme
        fields = (
            'sid', 'theme', 'weight', 'motivation', 'capacity', 'notes',
        )


class StoryDTSerializer(TOTOLOSerializer):
    description = serializers.CharField(source='description_short')

    class Meta:
        model = Story
        fields = (
            'weight', 'sid', 'title', 'date', 'description',
        )


class ThemeDTSerializer(TOTOLOSerializer):
    description = serializers.CharField(source='description_short')

    class Meta:
        model = Theme
        fields = (
            'weight', 'name', 'parents', 'description',
        )
