from rest_framework import serializers


class ImageUploadSerializer(serializers.Serializer):
    file = serializers.ImageField()

    def validate_file(self, value):
        if value.image.format.lower() not in ["png", "jpeg", "jpg"]:
            raise serializers.ValidationError(
                "Invalid file format. Only PNG, JPEG and JPG are supported."
            )
        return value
