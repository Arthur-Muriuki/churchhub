from django.contrib import admin
from .models import ChurchProfile


@admin.register(ChurchProfile)
class ChurchProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "email", "enable_confidential_pastoral_notes", "updated_at")

    def has_add_permission(self, request):
        return not ChurchProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False