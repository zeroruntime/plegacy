from django import forms
from .models import AdmissionRecord


class AdmissionRecordForm(forms.ModelForm):
    """
    Form for creating and editing admission records.
    All fields are user-editable except submitted_by and date_submitted.
    """
    
    class Meta:
        model = AdmissionRecord
        fields = [
            # Applicant Details
            'full_name',
            'date_of_birth',
            'gender',
            'nationality',
            'previous_school',
            'class_completed',
            
            # BECE Information
            'bece_index_number',
            'bece_year',
            'aggregate_score',
            'subjects_and_grades',
            
            # Program & Accommodation
            'program_applied_for',
            'accommodation_status',
            
            # Parent/Guardian Information
            'parent_name',
            'parent_relationship',
            'parent_occupation',
            'parent_contact',
            'parent_address',
            'parent_email',
            
            # Alumni Sponsorship
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
            
            # File Attachments
            'bece_results',
            'passport_photo',
            'birth_certificate',
            'medical_form',
            
            # Status
            'status',
        ]
        
        widgets = {
            # Applicant Details
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Full name of applicant',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'type': 'date',
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Applicant\'s nationality',
            }),
            'previous_school': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Previous basic school attended',
            }),
            'class_completed': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g., JHS 3, Primary 6',
            }),
            
            # BECE Information
            'bece_index_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'BECE Index Number',
            }),
            'bece_year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Year BECE was taken',
            }),
            'aggregate_score': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Aggregate score',
            }),
            'subjects_and_grades': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Subjects and grades (English, Math, Science, Social Studies, etc.)',
                'rows': 3,
            }),
            
            # Program & Accommodation
            'program_applied_for': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g., General Science, Business',
            }),
            'accommodation_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
            }),
            
            # Parent/Guardian Information
            'parent_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Full name',
            }),
            'parent_relationship': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g., Parent, Guardian',
            }),
            'parent_occupation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Occupation',
            }),
            'parent_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Phone number(s)',
            }),
            'parent_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Residential address',
                'rows': 2,
            }),
            'parent_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Email address',
            }),
            
            # Alumni Sponsorship
            'alumni_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Full name of PRESEC Old Boy',
            }),
            'alumni_year_group': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g., 1998, 2005',
            }),
            'alumni_class_stream': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g., Science 2, Business 1',
            }),
            'alumni_house': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'House at PRESEC',
            }),
            'alumni_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Phone number',
            }),
            'alumni_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Email address',
            }),
            'alumni_occupation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Current occupation/title',
            }),
            'alumni_organization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Current organization/institution',
            }),
            'alumni_relationship': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Relationship to applicant',
            }),
            'reason_for_recommendation': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Reason for recommendation',
                'rows': 3,
            }),
            
            # File Attachments
            'bece_results': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
            }),
            'passport_photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'accept': 'image/*',
            }),
            'birth_certificate': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
            }),
            'medical_form': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make medical_form optional
        self.fields['medical_form'].required = False
        # Make BECE results optional (will be uploaded later)
        self.fields['bece_results'].required = False
        self.fields['subjects_and_grades'].required = False
