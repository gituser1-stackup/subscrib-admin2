from django.contrib import admin
from .models import Licence, Application, AppUpdate, GitUpdate
# Register your models here.

admin.site.register(Licence)
admin.site.register(Application)
admin.site.register(AppUpdate)
admin.site.register(GitUpdate)