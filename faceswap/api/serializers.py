from rest_framework import serializers


class ImageUploadSerializer(serializers.Serializer):
    file = serializers.ImageField()

    def validate_file(self, value):
        if (image_format := value.image.format.lower()) not in [
            "png",
            "jpeg",
            "jpg",
            "mpo",
        ]:
            raise serializers.ValidationError(
                f"Invalid file format. Only PNG, JPEG and JPG are supported. "
                f"You specified: {image_format}"
            )
        return value
