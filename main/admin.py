from django.contrib import admin
from .models import OtherUser, GeneralUser, Region, RegionsAndUsers


@admin.register(OtherUser)
class OtherUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'username']
    search_fields = ['name']


@admin.register(GeneralUser)
class GeneralUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'username', 'role']
    list_filter = ['role']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name_region', 'service']
    list_filter = ['service']
    search_fields = ['name_region']


@admin.register(RegionsAndUsers)
class RegionsAndUsersAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_name', 'region', 'get_service', 'is_admin']
    list_filter = ['region']
    search_fields = ['region__name_region']


    def get_name(self, obj):
        return obj.username.name

    def get_service(self, obj):
        return obj.region.service


    get_name.short_description = 'Имя пользователя'
    get_service.short_description = 'Сервис'


