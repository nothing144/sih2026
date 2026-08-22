from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


# ============================================================
# OWNER REGISTRATION
# ============================================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
        ]

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
            role="EV_OWNER"
        )

        return user


# ============================================================
# USER PROFILE
# ============================================================

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
        ]

        read_only_fields = [
            "id",
            "username",
            "role",
        ]


# ============================================================
# OWNER LOGIN
# ============================================================

class OwnerLoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token["role"] = user.role

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        if self.user.role != "EV_OWNER":

            raise serializers.ValidationError(
                "This account is not an EV Owner."
            )

        data["user"] = UserSerializer(self.user).data

        return data


# ============================================================
# TESTER LOGIN
# ============================================================

class TesterLoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token["role"] = user.role

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        if self.user.role != "CERTIFIED_TESTER":

            raise serializers.ValidationError(
                "This account is not a Certified Tester."
            )

        data["user"] = UserSerializer(self.user).data

        return data