from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserProfile.Role.choices, default=UserProfile.Role.STUDENT, write_only=True)
    role_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'role', 'role_display']

    def get_role_display(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.get_role_display() if profile else 'Estudiante / Aprendiz'

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo.')
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', UserProfile.Role.STUDENT)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        profile = getattr(user, 'profile', None)
        if profile:
            profile.role = role
            profile.save(update_fields=['role', 'updated_at'])
        else:
            UserProfile.objects.create(user=user, role=role)
        return user
