from django.contrib import admin
from .models import Admin, MayorsPermit, IDCard, Mtop, Franchise, MayorsPermitTricycle, SuperAdmin, AdminPermission, MayorsPermitHistory, MayorsPermitTricycleHistory, ActivityLog


admin.site.register(Admin)
admin.site.register(MayorsPermit)
admin.site.register(IDCard)
admin.site.register(Mtop)
admin.site.register(Franchise)
admin.site.register(MayorsPermitTricycle)
admin.site.register(SuperAdmin)
admin.site.register(AdminPermission)
admin.site.register(MayorsPermitHistory)
admin.site.register(MayorsPermitTricycleHistory)
admin.site.register(ActivityLog)
