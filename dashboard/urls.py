from django.urls import path
from . import views
from .import_export_views import (
    ResourceExportView, ResourceImportView, ResourceSampleFileView,
    ProductExportView, ProductImportView, ProductSampleFileView,
    ResourceAlignmentExportView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Resource URLs
    path('resources/', views.ResourceListView.as_view(), name='resource-list'),
    path('resources/<int:pk>/', views.ResourceDetailView.as_view(), name='resource-detail'),
    path('resources/new/', views.ResourceCreateView.as_view(), name='resource-create'),
    path('resources/<int:pk>/edit/', views.ResourceUpdateView.as_view(), name='resource-update'),
    path('resources/<int:pk>/delete/', views.ResourceDeleteView.as_view(), name='resource-delete'),
    path('resources/import/', ResourceImportView.as_view(), name='resource-import'),
    path('resources/export/', ResourceExportView.as_view(), name='resource-export'),
    path('resources/sample-file/', ResourceSampleFileView.as_view(), name='resource-sample-file'),

    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/new/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('products/import/', ProductImportView.as_view(), name='product-import'),
    path('products/export/', ProductExportView.as_view(), name='product-export'),
    path('products/sample-file/', ProductSampleFileView.as_view(), name='product-sample-file'),

    # Product Documentation URLs
    path('products/<int:product_id>/documentation/new/', views.ProductDocumentationCreateView.as_view(), name='product-documentation-create'),
    path('documentation/<int:pk>/edit/', views.ProductDocumentationUpdateView.as_view(), name='product-documentation-update'),
    path('documentation/<int:pk>/delete/', views.ProductDocumentationDeleteView.as_view(), name='product-documentation-delete'),

    # Product Resource Assignment URLs
    path('products/<int:product_id>/assign/', views.assign_resource, name='assign-resource'),
    path('products/<int:product_id>/remove/<int:resource_id>/', views.remove_resource, name='remove-resource'),
    path('products/<int:product_id>/update-notes/<int:resource_id>/', views.update_resource_notes, name='update-resource-notes'),

    # Product Backup Resource Assignment URLs
    path('products/<int:product_id>/assign-backup/', views.assign_backup_resource, name='assign-backup-resource'),
    path('products/<int:product_id>/remove-backup/<int:resource_id>/', views.remove_backup_resource, name='remove-backup-resource'),
    path('products/<int:product_id>/update-backup-notes/<int:resource_id>/', views.update_backup_resource_notes, name='update-backup-resource-notes'),

    # Weekly Automation Updates URLs
    path('weekly-meetings/', views.WeeklyMeetingListView.as_view(), name='weekly-meeting-list'),
    path('weekly-meetings/<int:pk>/', views.WeeklyMeetingDetailView.as_view(), name='weekly-meeting-detail'),
    path('weekly-meetings/new/', views.WeeklyMeetingCreateView.as_view(), name='weekly-meeting-create'),
    path('weekly-meetings/<int:pk>/edit/', views.WeeklyMeetingUpdateView.as_view(), name='weekly-meeting-update'),
    path('weekly-meetings/<int:pk>/delete/', views.WeeklyMeetingDeleteView.as_view(), name='weekly-meeting-delete'),
    path('weekly-project-updates/<int:pk>/', views.WeeklyProjectUpdateDetailView.as_view(), name='weekly-project-update-detail'),
    path('weekly-project-updates/<int:pk>/edit/', views.WeeklyProjectUpdateEditView.as_view(), name='weekly-project-update-edit'),
    path('weekly-meetings/<int:pk>/start/', views.start_weekly_meeting, name='start-weekly-meeting'),
    path('weekly-meetings/<int:pk>/end/', views.end_weekly_meeting, name='end-weekly-meeting'),
    path('weekly-meetings/<int:meeting_id>/update-project/<int:project_id>/', views.update_project_in_meeting, name='update-project-in-meeting'),

    # Weekly Product Meeting URLs
    path('weekly-product-meetings/', views.WeeklyProductMeetingListView.as_view(), name='weekly-product-meeting-list'),
    path('weekly-product-meetings/<int:pk>/', views.WeeklyProductMeetingDetailView.as_view(), name='weekly-product-meeting-detail'),
    path('weekly-product-meetings/new/', views.WeeklyProductMeetingCreateView.as_view(), name='weekly-product-meeting-create'),
    path('weekly-product-meetings/<int:pk>/edit/', views.WeeklyProductMeetingUpdateView.as_view(), name='weekly-product-meeting-update'),
    path('weekly-product-meetings/<int:pk>/delete/', views.WeeklyProductMeetingDeleteView.as_view(), name='weekly-product-meeting-delete'),
    path('weekly-product-updates/<int:pk>/', views.WeeklyProductUpdateDetailView.as_view(), name='weekly-product-update-detail'),
    path('weekly-product-updates/<int:pk>/edit/', views.WeeklyProductUpdateEditView.as_view(), name='weekly-product-update-edit'),
    path('weekly-product-meetings/<int:pk>/start/', views.start_weekly_product_meeting, name='start-weekly-product-meeting'),
    path('weekly-product-meetings/<int:pk>/end/', views.end_weekly_product_meeting, name='end-weekly-product-meeting'),
    path('weekly-product-meetings/<int:meeting_id>/update-product/<int:project_id>/', views.update_product_in_meeting, name='update-product-in-meeting'),
    path('weekly-product-meetings/latest-updates/', views.LatestProductUpdatesView.as_view(), name='latest-product-updates'),

    # Quarter URLs
    path('quarters/', views.QuarterListView.as_view(), name='quarter-list'),
    path('quarters/<int:pk>/', views.QuarterDetailView.as_view(), name='quarter-detail'),
    path('quarters/new/', views.QuarterCreateView.as_view(), name='quarter-create'),
    path('quarters/<int:pk>/edit/', views.QuarterUpdateView.as_view(), name='quarter-update'),
    path('quarters/<int:pk>/delete/', views.QuarterDeleteView.as_view(), name='quarter-delete'),

    # Quarter Target URLs
    path('quarters/<int:quarter_id>/targets/', views.QuarterTargetListView.as_view(), name='quarter-target-list'),
    path('targets/<int:pk>/', views.QuarterTargetDetailView.as_view(), name='quarter-target-detail'),
    path('quarters/<int:quarter_id>/targets/new/', views.QuarterTargetCreateView.as_view(), name='quarter-target-create'),
    path('targets/<int:pk>/edit/', views.QuarterTargetUpdateView.as_view(), name='quarter-target-update'),
    path('targets/<int:pk>/delete/', views.QuarterTargetDeleteView.as_view(), name='quarter-target-delete'),

    # Quarter Target Resource Assignment URLs
    path('targets/<int:target_id>/assign/', views.assign_resource_to_target, name='assign-resource-to-target'),
    path('targets/<int:target_id>/remove/<int:resource_id>/', views.remove_resource_from_target, name='remove-resource-from-target'),

    # Quarter Timeline and Completion URLs
    path('quarters/timeline/', views.QuarterTimelineView.as_view(), name='quarter-timeline'),
    path('quarters/<int:pk>/complete/', views.complete_quarter, name='quarter-complete'),
    path('quarters/<int:pk>/summary/', views.quarter_summary, name='quarter-summary'),
    path('quarters/dashboard/', views.QuarterTargetDashboardView.as_view(), name='quarter-target-dashboard'),

    # Resource Planning URLs
    path('resource-planning/', views.ResourcePlanningView.as_view(), name='resource-planning'),
    path('resource-leaves/new/', views.ResourceLeaveCreateView.as_view(), name='resource-leave-create'),
    path('resource-leaves/<int:pk>/edit/', views.ResourceLeaveUpdateView.as_view(), name='resource-leave-update'),
    path('resource-leaves/<int:pk>/delete/', views.ResourceLeaveDeleteView.as_view(), name='resource-leave-delete'),
    path('resource-planning/assign/<int:project_id>/', views.assign_resource_with_dates, name='assign-resource-with-dates'),
    path('resource-planning/edit/<int:project_id>/<int:resource_id>/', views.edit_resource_allocation, name='edit-resource-allocation'),
    path('resource-planning/remove/<int:project_id>/<int:resource_id>/', views.remove_resource_from_planning, name='remove-resource-from-planning'),

    # Rock Management URLs
    path('rocks/', views.RockListView.as_view(), name='rock-list'),
    path('rocks/<int:pk>/', views.RockDetailView.as_view(), name='rock-detail'),
    path('rocks/new/', views.RockCreateView.as_view(), name='rock-create'),
    path('rocks/<int:pk>/edit/', views.RockUpdateView.as_view(), name='rock-update'),
    path('rocks/<int:pk>/delete/', views.RockDeleteView.as_view(), name='rock-delete'),
    path('rocks/<int:pk>/start/', views.start_rock, name='start-rock'),
    path('rocks/<int:pk>/complete/', views.complete_rock, name='complete-rock'),
    path('rocks/dashboard/', views.RockDashboardView.as_view(), name='rock-dashboard'),
    path('resources/<int:resource_id>/assign-rock/', views.assign_rock, name='assign-rock'),

    # Strategic Roadmap URLs - Temporarily hidden
    # path('roadmap/', views.RoadmapTimelineView.as_view(), name='roadmap-timeline'),
    # path('roadmap/quarter/<int:quarter_id>/', views.RoadmapTimelineView.as_view(), name='roadmap-timeline-quarter'),
    # path('roadmap/items/', views.RoadmapItemListView.as_view(), name='roadmap-item-list'),
    # path('roadmap/items/<int:pk>/', views.RoadmapItemDetailView.as_view(), name='roadmap-item-detail'),
    # path('roadmap/items/new/', views.RoadmapItemCreateView.as_view(), name='roadmap-item-create'),
    # path('roadmap/items/new/quarter/<int:quarter_id>/', views.RoadmapItemCreateView.as_view(), name='roadmap-item-create-quarter'),
    # path('roadmap/items/<int:pk>/edit/', views.RoadmapItemUpdateView.as_view(), name='roadmap-item-update'),
    # path('roadmap/items/<int:pk>/delete/', views.RoadmapItemDeleteView.as_view(), name='roadmap-item-delete'),
    # path('roadmap/items/<int:pk>/start/', views.start_roadmap_item, name='start-roadmap-item'),
    # path('roadmap/items/<int:pk>/complete/', views.complete_roadmap_item, name='complete-roadmap-item'),
    # path('roadmap/items/<int:pk>/update-progress/', views.update_roadmap_item_progress, name='update-roadmap-item-progress'),
    # path('roadmap/items/<int:pk>/update-dates/', views.update_roadmap_item_dates, name='update-roadmap-item-dates'),

    # Production Bugs Management URLs
    path('production-bugs/', views.ProductionBugListView.as_view(), name='production-bug-list'),
    path('production-bugs/<int:pk>/', views.ProductionBugDetailView.as_view(), name='production-bug-detail'),
    path('production-bugs/new/', views.ProductionBugCreateView.as_view(), name='production-bug-create'),
    path('production-bugs/<int:pk>/edit/', views.ProductionBugUpdateView.as_view(), name='production-bug-update'),
    path('production-bugs/<int:pk>/delete/', views.ProductionBugDeleteView.as_view(), name='production-bug-delete'),

    # Documentation Management URLs
    path('documentation/', views.ProductDocumentationListView.as_view(), name='product-documentation-list'),
    path('department-documents/', views.DepartmentDocumentListView.as_view(), name='department-document-list'),
    path('department-documents/new/', views.DepartmentDocumentCreateView.as_view(), name='department-document-create'),
    path('department-documents/<int:pk>/edit/', views.DepartmentDocumentUpdateView.as_view(), name='department-document-update'),
    path('department-documents/<int:pk>/delete/', views.DepartmentDocumentDeleteView.as_view(), name='department-document-delete'),

    # Records Section URLs - Temporarily hidden
    # path('records/', views.RecordsListView.as_view(), name='records-list'),
    # path('records/password-verify/', views.RecordsPasswordVerifyView.as_view(), name='records-password-verify'),
    # path('records/password-set/', views.RecordsPasswordSetView.as_view(), name='records-password-set'),
    # path('records/restore/<int:pk>/', views.restore_record, name='restore-record'),

    # User Action Logs
    path('logs/', views.UserActionListView.as_view(), name='user-action-list'),

    # Resource Alignment
    path('resource-alignment/', views.ResourceAlignmentView.as_view(), name='resource-alignment'),
    path('resource-alignment/export/', ResourceAlignmentExportView.as_view(), name='resource-alignment-export'),

    # KPI Management URLs
    path('kpi-management/', views.KPIManagementView.as_view(), name='kpi-management'),
    path('kpi-management/resources/<int:resource_id>/kpis/', views.ResourceKPIListView.as_view(), name='resource-kpi-list'),
    path('kpi-management/resources/<int:resource_id>/kpis/new/', views.KPICreateView.as_view(), name='kpi-create'),
    path('kpi-management/kpis/<int:pk>/', views.KPIDetailView.as_view(), name='kpi-detail'),
    path('kpi-management/kpis/<int:pk>/edit/', views.KPIUpdateView.as_view(), name='kpi-update'),
    path('kpi-management/kpis/<int:pk>/delete/', views.KPIDeleteView.as_view(), name='kpi-delete'),
    path('kpi-management/resources/<int:resource_id>/rate/<int:year>/<int:month>/', views.KPIRatingView.as_view(), name='kpi-rating'),
    path('kpi-management/resources/<int:resource_id>/submissions/', views.KPIRatingSubmissionListView.as_view(), name='kpi-submission-list'),
    path('kpi-management/submissions/<int:pk>/', views.KPIRatingSubmissionDetailView.as_view(), name='kpi-submission-detail'),

    # 1:1 Feedback URLs
    path('one-on-one-feedbacks/', views.OneOnOneFeedbackListView.as_view(), name='one-on-one-feedback-list'),
    path('one-on-one-feedbacks/<int:pk>/', views.OneOnOneFeedbackDetailView.as_view(), name='one-on-one-feedback-detail'),
    path('one-on-one-feedbacks/new/', views.OneOnOneFeedbackCreateView.as_view(), name='one-on-one-feedback-create'),
    path('one-on-one-feedbacks/<int:pk>/edit/', views.OneOnOneFeedbackUpdateView.as_view(), name='one-on-one-feedback-update'),
    path('one-on-one-feedbacks/<int:pk>/delete/', views.OneOnOneFeedbackDeleteView.as_view(), name='one-on-one-feedback-delete'),

    # Monthly Feedback URLs
    path('monthly-feedback/', views.MonthlyFeedbackListView.as_view(), name='monthly-feedback-list'),
    path('monthly-feedback/history/', views.MonthlyFeedbackHistoryView.as_view(), name='monthly-feedback-history-view'),
    path('monthly-feedback/<int:pk>/', views.MonthlyFeedbackDetailView.as_view(), name='monthly-feedback-detail'),
    path('monthly-feedback/new/', views.MonthlyFeedbackCreateView.as_view(), name='monthly-feedback-create'),
    path('monthly-feedback/<int:pk>/edit/', views.MonthlyFeedbackUpdateView.as_view(), name='monthly-feedback-update'),

    # SOP Management URLs
    path('sop-management/', views.SOPListView.as_view(), name='sop-list'),
    path('sop-management/<int:pk>/', views.SOPDetailView.as_view(), name='sop-detail'),
    path('sop-management/new/', views.SOPCreateView.as_view(), name='sop-create'),
    path('sop-management/<int:pk>/edit/', views.SOPUpdateView.as_view(), name='sop-update'),
    path('sop-management/<int:pk>/status/', views.SOPStatusUpdateView.as_view(), name='sop-status-update'),

    # Automation Runner URLs
    path('automation-runners/', views.AutomationRunnerListView.as_view(), name='automation-runner-list'),
    path('automation-runners/<int:pk>/', views.AutomationRunnerDetailView.as_view(), name='automation-runner-detail'),
    path('automation-runners/new/', views.AutomationRunnerCreateView.as_view(), name='automation-runner-create'),
    path('automation-runners/<int:pk>/edit/', views.AutomationRunnerUpdateView.as_view(), name='automation-runner-update'),
    path('automation-runners/<int:pk>/delete/', views.AutomationRunnerDeleteView.as_view(), name='automation-runner-delete'),

    # Automation Sprint URLs - Updated for better URL resolution
    path('automation-sprints/', views.AutomationSprintListView.as_view(), name='automation-sprint-list'),
    path('automation-sprints/<int:pk>/', views.AutomationSprintDetailView.as_view(), name='automation-sprint-detail'),
    path('automation-sprints/new/', views.AutomationSprintCreateView.as_view(), name='automation-sprint-create'),
    path('automation-sprints/<int:pk>/edit/', views.AutomationSprintUpdateView.as_view(), name='automation-sprint-update'),
    path('automation-sprints/<int:pk>/delete/', views.AutomationSprintDeleteView.as_view(), name='automation-sprint-delete'),
    path('automation-sprints/<int:pk>/metrics/', views.SprintMetricsUpdateView.as_view(), name='automation-sprint-metrics'),

    # User Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('link-user-resource/', views.link_user_to_resource, name='link-user-resource'),

    # Password Change
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='dashboard/password_change_form.html',
             success_url='/dashboard/password-change/done/'
         ), 
         name='password_change'),
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='dashboard/password_change_done.html'
         ), 
         name='password_change_done'),
]
