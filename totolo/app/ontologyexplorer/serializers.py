# Copyright 2022, themeontology.org
# Tests:
from rest_framework import serializers
from .models import Theme


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = (
            'score', 'name', 'parents', 'description',
        )
