from django.contrib import admin
from .models import Chat, Memory, Biographyitem

# Register your models here.


class MemoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_username', 'content', 'description')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'username'  

admin.site.register(Chat)
# admin.site.register(Memory)
admin.site.register(Biographyitem)
admin.site.register(Memory, MemoryAdmin)