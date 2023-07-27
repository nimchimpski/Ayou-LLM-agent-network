from django.contrib import admin
from .models import Chat, Memory, Biographyitem

# Register your models here.
admin.site.register(Chat)
admin.site.register(Memory)
admin.site.register(Biographyitem)