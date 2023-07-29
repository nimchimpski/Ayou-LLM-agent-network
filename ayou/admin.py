from django.contrib import admin
from .models import Chat, Memory, Biographyitem, Domain
# Register your models here.


class MemoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_username', 'content', 'description')

    def get_username(self, obj):
        if obj.user is not None:
            return obj.user.username
        else:
            return 'None'
    get_username.short_description = 'username'  

admin.site.register(Chat)
admin.site.register(Biographyitem)
admin.site.register(Memory, MemoryAdmin)
admin.site.register(Domain)