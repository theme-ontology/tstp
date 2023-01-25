# Copyright 2022, themeontology.org
# Tests:
from rest_framework import serializers
from .models import Theme, Story, StoryTheme


class TOTOLOSerializer(serializers.ModelSerializer):
    weight = serializers.SerializerMethodField()
    relation = serializers.SerializerMethodField()

    def __init__(self, *args, weight_index=None, relation_index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._weight_index = weight_index
        self._relation_index = relation_index

    def get_weight(self, instance):
        if self._weight_index and instance:
            return self._weight_index[instance.idx]
        return 0

    def get_relation(self, instance):
        if self._relation_index and instance:
            return self._relation_index.get(instance.idx, '')
        return ''


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


class StorySearchDTSerializer(TOTOLOSerializer):
    description = serializers.CharField(source='description_short')

    class Meta:
        model = Story
        fields = (
            'weight', 'sid', 'title', 'date', 'description',
        )


class ThemeSearchDTSerializer(TOTOLOSerializer):
    description = serializers.CharField(source='description_short')

    class Meta:
        model = Theme
        fields = (
            'weight', 'name', 'parents', 'description',
        )


class ThemeRelativesDTSerializer(TOTOLOSerializer):
    description = serializers.CharField(source='description_short')

    class Meta:
        model = Theme
        fields = (
            'relation', 'name', 'parents', 'description',
        )


