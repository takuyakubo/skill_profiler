from django.contrib import admin
from user_profile.models import UProfile
# Register your models here.


class UProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(UProfile, UProfileAdmin)
