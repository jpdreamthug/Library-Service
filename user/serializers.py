from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used for creating and updating user instances. It
    includes    custom error messages for validation errors. The `create`
     method is responsible for creating a new user with an encrypted
     password, while the `update` method updates an existing user
      instance and sets the password correctly.

    Fields:
        id: The unique identifier for the user. Read-only.
        email: The user's email address. Required.
        password: The user's password. Must be at least 5 characters
                  long and is write-only.
        first_name: The user's first name. Optional.
        last_name: The user's last name. Optional.
        is_staff: Indicates whether the user has staff permissions. Read-only.

    Error Messages:
        password:
            min_length: "The password must be at least 5 characters long."
        email:
            required: "Email address is required."
            blank: "Email address cannot be blank."
            invalid: "Enter a valid email address."

    Methods:
        create: Creates a new user with the validated data.
                Encrypts the password before saving.
        update: Updates an existing user with the validated data.
                Sets the new password if provided.
    """

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_staff",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "error_messages": {
                    "min_length": "Ensure this field has at least "
                                  "5 characters."
                }
            },
            "email": {
                "error_messages": {
                    "required": "Email address is required.",
                    "blank": "Email address cannot be blank.",
                    "invalid": "Enter a valid email address."
                }
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a user, set the password correctly and return it
        """
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user
