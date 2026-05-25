from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Perfil mínimo para separar los tableros por tipo de usuario."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        MANAGER = 'manager', 'Gestor del conocimiento'
        TUTOR = 'tutor', 'Tutor / Docente'
        STUDENT = 'student', 'Estudiante / Aprendiz'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    institution = models.CharField(max_length=180, blank=True, default='')
    program = models.CharField(max_length=180, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'


def get_or_create_profile(user):
    """Garantiza que cualquier usuario antiguo o superusuario tenga perfil."""
    default_role = UserProfile.Role.ADMIN if getattr(user, 'is_superuser', False) else UserProfile.Role.STUDENT
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': default_role})
    if user.is_superuser and profile.role != UserProfile.Role.ADMIN:
        profile.role = UserProfile.Role.ADMIN
        profile.save(update_fields=['role', 'updated_at'])
    return profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        default_role = UserProfile.Role.ADMIN if instance.is_superuser else UserProfile.Role.STUDENT
        UserProfile.objects.get_or_create(user=instance, defaults={'role': default_role})
