from django.contrib import admin
from .models import Resource, Project, ProjectResource, SprintCycle, OATReleaseCycle, WeeklyMeeting, WeeklyProjectUpdate, Quarter, QuarterTarget, QuarterTargetResource, WeeklyProductMeeting, WeeklyProductUpdate, ResourceLeave, ProductionBug, RecordsPassword, DeletedRecord, UserAction, AutomationSprint

# Register your models here.
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'availability', 'user', 'created_at')
    list_filter = ('availability', 'role')
    search_fields = ('name', 'email', 'role', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule', 'in_production', 'in_development', 'created_at')
    list_filter = ('status', 'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule', 'in_production', 'in_development')
    search_fields = ('name', 'description', 'automation_framework_tech_stack')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'status', 'team_lead')
        }),
        ('Automation Status', {
            'fields': ('smoke_automation_status', 'regression_automation_status', 'pipeline_schedule', 'in_production', 'in_development')
        }),
        ('Test Cases', {
            'fields': ('total_number_of_available_test_cases', 'total_automatable_test_cases', 'total_automated_test_cases', 
                      'total_automatable_smoke_test_cases', 'total_automated_smoke_test_cases', 
                      'total_number_of_functional_test_cases', 'total_number_of_business_test_cases')
        }),
        ('Automation Details', {
            'fields': ('execution_time_of_smoke', 'status_of_last_automation_run', 'date_of_last_automation_run', 
                      'automation_framework_tech_stack', 'regression_coverage', 'bugs_found_through_automation',
                      'sprint_cycle', 'oat_release_cycle')
        }),
    )

@admin.register(ProjectResource)
class ProjectResourceAdmin(admin.ModelAdmin):
    list_display = ('project', 'resource', 'assigned_date', 'hours_allocated')
    list_filter = ('assigned_date',)
    search_fields = ('project__name', 'resource__name')
    date_hierarchy = 'assigned_date'

@admin.register(SprintCycle)
class SprintCycleAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'description')
    list_filter = ('active',)
    search_fields = ('name', 'description')

@admin.register(OATReleaseCycle)
class OATReleaseCycleAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'description')
    list_filter = ('active',)
    search_fields = ('name', 'description')

class WeeklyProjectUpdateInline(admin.TabularInline):
    model = WeeklyProjectUpdate
    extra = 0
    fields = ('project', 'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule', 
              'execution_time_hours', 'execution_time_minutes', 'total_automated_test_cases', 'bugs_found_through_automation')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('project', 'sprint_cycle', 'oat_release_cycle', 'team_lead')

@admin.register(WeeklyMeeting)
class WeeklyMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_date', 'is_completed', 'project_count', 'created_at')
    list_filter = ('is_completed', 'meeting_date')
    search_fields = ('title', 'notes')
    date_hierarchy = 'meeting_date'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WeeklyProjectUpdateInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'meeting_date', 'notes', 'is_completed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(WeeklyProjectUpdate)
class WeeklyProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ('project', 'meeting', 'smoke_automation_status', 'regression_automation_status', 
                   'total_automated_test_cases', 'bugs_found_through_automation', 'created_at')
    list_filter = ('meeting', 'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule')
    search_fields = ('project__name', 'meeting__title', 'last_automation_run_status')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Meeting Information', {
            'fields': ('meeting', 'project')
        }),
        ('Automation Status', {
            'fields': ('smoke_automation_status', 'regression_automation_status', 'pipeline_schedule')
        }),
        ('Test Cases', {
            'fields': ('total_available_test_cases', 'total_automatable_test_cases', 'total_automated_test_cases', 
                      'total_automated_smoke_test_cases', 'functional_test_cases_count', 'business_test_cases_count')
        }),
        ('Automation Details', {
            'fields': ('execution_time_hours', 'execution_time_minutes', 'last_automation_run_status', 'last_automation_run_date', 
                      'automation_framework_tech_stack', 'regression_coverage', 'bugs_found_through_automation',
                      'sprint_cycle', 'oat_release_cycle', 'team_lead')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

class WeeklyProductUpdateInline(admin.TabularInline):
    model = WeeklyProductUpdate
    extra = 0
    fields = ('project', 'notes', 'problems', 'expected_solution', 'solution_timeline')

@admin.register(WeeklyProductMeeting)
class WeeklyProductMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_date', 'is_completed', 'product_count', 'created_at')
    list_filter = ('is_completed', 'meeting_date')
    search_fields = ('title', 'notes')
    date_hierarchy = 'meeting_date'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WeeklyProductUpdateInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'meeting_date', 'notes', 'is_completed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(WeeklyProductUpdate)
class WeeklyProductUpdateAdmin(admin.ModelAdmin):
    list_display = ('project', 'meeting', 'solution_timeline', 'created_at')
    list_filter = ('meeting', 'solution_timeline')
    search_fields = ('project__name', 'meeting__title', 'notes', 'problems', 'expected_solution')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Meeting Information', {
            'fields': ('meeting', 'project')
        }),
        ('Product Details', {
            'fields': ('notes', 'problems', 'expected_solution', 'solution_timeline')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

class QuarterTargetResourceInline(admin.TabularInline):
    model = QuarterTargetResource
    extra = 0
    fields = ('resource', 'allocation_percentage', 'notes')

@admin.register(Quarter)
class QuarterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'year', 'quarter_number', 'start_date', 'end_date', 'completed', 'completion_date')
    list_filter = ('year', 'quarter_number', 'completed')
    search_fields = ('name', 'completion_notes')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Quarter Information', {
            'fields': ('year', 'quarter_number', 'name', 'start_date', 'end_date')
        }),
        ('Completion Status', {
            'fields': ('completed', 'completion_date', 'completion_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(QuarterTarget)
class QuarterTargetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quarter', 'project', 'target_value', 'achieved_value', 'achievement_percentage')
    list_filter = ('quarter', 'project')
    search_fields = ('target_description', 'achievement_notes', 'project__name')
    readonly_fields = ('achievement_percentage', 'created_at', 'updated_at')
    inlines = [QuarterTargetResourceInline]

    fieldsets = (
        ('Target Information', {
            'fields': ('quarter', 'project', 'target_description')
        }),
        ('Target Values', {
            'fields': ('target_value', 'achieved_value', 'achievement_percentage', 'achievement_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(QuarterTargetResource)
class QuarterTargetResourceAdmin(admin.ModelAdmin):
    list_display = ('quarter_target', 'resource', 'allocation_percentage')
    list_filter = ('quarter_target__quarter', 'resource')
    search_fields = ('quarter_target__project__name', 'resource__name', 'notes')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Assignment Information', {
            'fields': ('quarter_target', 'resource', 'allocation_percentage', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResourceLeave)
class ResourceLeaveAdmin(admin.ModelAdmin):
    list_display = ('resource', 'leave_type', 'start_date', 'end_date')
    list_filter = ('leave_type', 'resource')
    search_fields = ('resource__name', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Leave Information', {
            'fields': ('resource', 'leave_type', 'start_date', 'end_date', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductionBug)
class ProductionBugAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'severity', 'reported_date', 'resolved_date', 'test_case_added')
    list_filter = ('status', 'severity', 'test_case_added', 'reported_date', 'resolved_date')
    search_fields = ('title', 'project__name', 'details')
    date_hierarchy = 'reported_date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Bug Information', {
            'fields': ('title', 'project', 'status', 'severity', 'test_case_added')
        }),
        ('Dates', {
            'fields': ('reported_date', 'resolved_date')
        }),
        ('Links', {
            'fields': ('gops_board_link', 'product_board_link')
        }),
        ('Details', {
            'fields': ('details',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RecordsPassword)
class RecordsPasswordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Password Settings', {
            'fields': ('password',),
            'description': 'Set the password for accessing the Records section. This password will be required to view and restore deleted records.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Only allow adding if no RecordsPassword exists yet
        return not RecordsPassword.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the password record
        return False


@admin.register(DeletedRecord)
class DeletedRecordAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'record_id', 'deleted_at', 'deleted_by')
    list_filter = ('model_name', 'deleted_at')
    search_fields = ('model_name', 'record_id', 'data')
    date_hierarchy = 'deleted_at'
    readonly_fields = ('model_name', 'record_id', 'data', 'deleted_at', 'deleted_by')

    fieldsets = (
        ('Record Information', {
            'fields': ('model_name', 'record_id', 'deleted_by', 'deleted_at')
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent manual addition of deleted records
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent editing of deleted records
        return False


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'model_name', 'record_id', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'user', 'timestamp', 'model_name')
    search_fields = ('user__username', 'model_name', 'details', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'action_type', 'model_name', 'record_id', 'details', 'ip_address', 'timestamp')

    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'action_type', 'timestamp', 'ip_address')
        }),
        ('Related Object', {
            'fields': ('model_name', 'record_id')
        }),
        ('Details', {
            'fields': ('details',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent manual addition of user actions
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent editing of user actions
        return False


@admin.register(AutomationSprint)
class AutomationSprintAdmin(admin.ModelAdmin):
    list_display = ('product', 'engineering_manager_name', 'sprint_length', 'start_date', 'status', 'dev_training_status', 'created_at')
    list_filter = ('status', 'sprint_length', 'sprint_type', 'dev_training_status', 'start_date')
    search_fields = ('product__name', 'engineering_manager_name', 'rationale', 'notes')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Sprint Information', {
            'fields': ('product', 'engineering_manager_name', 'sprint_length', 'total_dev_resources', 'sprint_type', 'start_date', 'status')
        }),
        ('Sprint Details', {
            'fields': ('rationale', 'risks', 'qa_point_of_contact', 'dev_training_status', 'notes')
        }),
        ('Progress Tracking', {
            'fields': ('total_sprint_days', 'total_planned_working_hours', 'blocked_hours', 'total_planned_test_cases', 'total_test_cases_automated')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
