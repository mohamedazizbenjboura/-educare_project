from django.contrib import admin
from .models import User, Student, AttendanceRecord, InterventionCase, SystemConfiguration, ActionLog

admin.site.register(User)
admin.site.register(Student)
admin.site.register(AttendanceRecord)
admin.site.register(InterventionCase)

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('absence_threshold',)

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action_detail', 'result')
