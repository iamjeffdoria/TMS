from django.contrib import admin
from .models import Admin, MayorsPermit, IDCard, Mtop, Franchise, MayorsPermitTricycle, SuperAdmin


admin.site.register(Admin)
admin.site.register(MayorsPermit)
admin.site.register(IDCard)
admin.site.register(Mtop)
admin.site.register(Franchise)
admin.site.register(MayorsPermitTricycle)
admin.site.register(SuperAdmin)