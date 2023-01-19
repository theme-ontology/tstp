# Copyright 2022, themeontology.org
# Tests:
from rest_framework import serializers
from .models import Theme, Story, StoryTheme


class StorySerializer(serializers.ModelSerializer):
    weight = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = (
            'sid', 'title', 'date', 'parents', 'children', 'description', 'source', 'ratings', 'weight',
        )

    def __init__(self, *args, weight_index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._weight_index = weight_index

    def get_weight(self, instance):
        if self._weight_index and instance:
            return self._weight_index[instance.idx]
        return 42


class ThemeSerializer(serializers.ModelSerializer):
    weight = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        fields = (
            'name', 'parents', 'children', 'description', 'source', 'weight',
        )

    def get_weight(self, instance):
        return 42


class StoryThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryTheme
        fields = (
            'sid', 'theme', 'weight', 'motivation', 'capacity', 'notes',
        )
