import logging

from rest_framework import generics, status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ImageUploadSerializer
from .utils import get_task_position, save_file, create_task

logger = logging.getLogger(__name__)


class ImageUploadView(generics.CreateAPIView):
    serializer_class = ImageUploadSerializer

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        file_path = save_file(file)
        task = create_task(file_path)
        return Response(
            {"task_id": str(task.id)}, status=status.HTTP_201_CREATED
        )


class TaskStatusView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        task_id = kwargs.get("task_id")
        task_status = get_task_position(task_id)
        if task_status is None:
            raise exceptions.NotFound("Task not found")
        return Response(task_status, status=status.HTTP_200_OK)


class HealthView(APIView):
    def get(self, *_, **__):
        return Response("ok")
