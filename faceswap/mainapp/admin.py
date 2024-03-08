from django.contrib import admin

from .models import Video, VideoGenerationCount


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "video_file", "show"]
    list_editable = ["show"]


@admin.register(VideoGenerationCount)
class VideoGenerationCountAdmin(admin.ModelAdmin):
    readonly_fields = ["count"]
    list_display = ["count"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
