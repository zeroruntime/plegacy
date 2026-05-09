from django.contrib import admin
from .models import AdmissionRecord


@admin.register(AdmissionRecord)
class AdmissionRecordAdmin(admin.ModelAdmin):
    """
    Admin interface for AdmissionRecord model.
    """
    list_display = [
        'full_name',
        'program_applied_for',
        'accommodation_status',
        'submitted_by',
        'date_submitted',
    ]
    
    list_filter = [
        'date_submitted',
        'program_applied_for',
        'accommodation_status',
        'submitted_by__year_group',
        'submitted_by',
    ]
    
    search_fields = [
        'full_name',
        'bece_index_number',
        'alumni_name',
        'submitted_by__username',
    ]
    
    readonly_fields = [
        'submitted_by',
        'date_submitted',
    ]
    
    fieldsets = (
        ('Applicant Information', {
            'fields': (
                'full_name',
                'date_of_birth',
                'gender',
                'nationality',
                'previous_school',
                'class_completed',
            )
        }),
        ('BECE Information', {
            'fields': (
                'bece_index_number',
                'bece_year',
                'aggregate_score',
                'subjects_and_grades',
            )
        }),
        ('Program & Accommodation', {
            'fields': (
                'program_applied_for',
                'accommodation_status',
            )
        }),
        ('Parent/Guardian Information', {
            'fields': (
                'parent_name',
                'parent_relationship',
                'parent_occupation',
                'parent_contact',
                'parent_address',
                'parent_email',
            )
        }),
        ('Alumni Sponsorship/Endorsement', {
            'fields': (
                'alumni_name',
                'alumni_year_group',
                'alumni_class_stream',
                'alumni_house',
                'alumni_phone',
                'alumni_email',
                'alumni_occupation',
                'alumni_organization',
                'alumni_relationship',
                'reason_for_recommendation',
            )
        }),
        ('File Attachments', {
            'fields': (
                'bece_results',
                'passport_photo',
                'birth_certificate',
                'medical_form',
            )
        }),
        ('Administrative', {
            'fields': (
                'submitted_by',
                'date_submitted',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Automatically set submitted_by to the current user when creating."""
        if not change:  # Only on creation
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)
