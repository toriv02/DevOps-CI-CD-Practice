from django.contrib import admin

from project.models import *

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display=['id','name','type']

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display=['id','name']