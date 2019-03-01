from django.contrib import admin
from blog.models import Blog, Comment, Reference
# Register your models here.
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Reference)