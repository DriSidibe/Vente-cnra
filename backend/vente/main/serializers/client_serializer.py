
from django.contrib.auth.models import User
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'is_active',
            'is_superuser',
        ]

        read_only_fields = [
            'id',
            'is_superuser',
        ]

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate_username(self, value):
        username = value.strip()

        utilisateurs = User.objects.filter(
            username__iexact=username
        )

        if self.instance:
            utilisateurs = utilisateurs.exclude(
                pk=self.instance.pk
            )

        if utilisateurs.exists():
            raise serializers.ValidationError(
                "Ce nom d'utilisateur est déjà utilisé."
            )

        if not username:
            raise serializers.ValidationError(
                "Le nom d'utilisateur est obligatoire."
            )

        return username

    def validate_email(self, value):
        email = value.strip().lower()

        utilisateurs = User.objects.filter(
            email__iexact=email
        )

        if self.instance:
            utilisateurs = utilisateurs.exclude(
                pk=self.instance.pk
            )

        if utilisateurs.exists():
            raise serializers.ValidationError(
                "Cette adresse e-mail est déjà utilisée."
            )

        return email

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        if not password:
            raise serializers.ValidationError({
                'password': "Le mot de passe est obligatoire."
            })

        client = User(**validated_data)

        client.set_password(password)

        # Un compte client ne peut pas devenir administrateur.
        client.is_staff = False
        client.is_superuser = False

        client.save()

        return client

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attribut, valeur in validated_data.items():
            setattr(instance, attribut, valeur)

        if password:
            instance.set_password(password)

        # Protection contre la modification du rôle.
        instance.is_staff = False
        instance.is_superuser = False

        instance.save()

        return instance
