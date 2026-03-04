from django.contrib import admin
from .models import Post
from .models import Artwork


admin.site.register(Post)
admin.site.register(Artwork)

from .models import MailingListSubscriber

@admin.register(MailingListSubscriber)
class MailingListSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "is_active", "created_at", "source")
    list_filter = ("is_active", "created_at")
    search_fields = ("email", "first_name")
