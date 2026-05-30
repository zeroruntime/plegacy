from django import forms
from .models import AdmissionRecord
from .choices import (
    ALUMNI_HOUSE_CHOICES,
    ALUMNI_RELATIONSHIP_CHOICES,
    ALUMNI_YEAR_GROUP_CHOICES,
    BECE_SUBJECTS,
    PARENT_RELATIONSHIP_CHOICES,
    PROGRAM_CHOICES,
    choice_list_with_blank,
)


FIELD_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'


def subject_grade_field_name(index):
    return f'subject_grade_{index}'


def parse_subject_grades(value):
    grades = {}
    for line in (value or '').splitlines():
        if ':' not in line:
            continue
        subject, grade = line.split(':', 1)
        grades[subject.strip().upper()] = grade.strip()
    return grades


class AdmissionRecordForm(forms.ModelForm):
    """
    Form for creating and editing admission records.
    All fields are user-editable except submitted_by and date_submitted.
    """
    
    program_applied_for = forms.ChoiceField(
        choices=choice_list_with_blank(PROGRAM_CHOICES, 'Select program'),
        widget=forms.Select(attrs={'class': FIELD_CLASS}),
    )
    parent_relationship = forms.ChoiceField(
        choices=choice_list_with_blank(PARENT_RELATIONSHIP_CHOICES, 'Select relationship'),
        widget=forms.Select(attrs={'class': FIELD_CLASS}),
    )
    alumni_year_group = forms.ChoiceField(
        choices=choice_list_with_blank(ALUMNI_YEAR_GROUP_CHOICES, 'Select year group'),
        widget=forms.Select(attrs={'class': FIELD_CLASS}),
    )
    alumni_house = forms.ChoiceField(
        choices=choice_list_with_blank(ALUMNI_HOUSE_CHOICES, 'Select house'),
        widget=forms.Select(attrs={'class': FIELD_CLASS}),
    )
    alumni_relationship = forms.ChoiceField(
        choices=choice_list_with_blank(ALUMNI_RELATIONSHIP_CHOICES, 'Select relationship'),
        widget=forms.Select(attrs={'class': FIELD_CLASS}),
    )

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
            'subjects_and_grades': forms.HiddenInput(),
            
            # Program & Accommodation
            'accommodation_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
            }),
            
            # Parent/Guardian Information
            'parent_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Full name',
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
            'alumni_class_stream': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g., Science 2, Business 1',
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
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make medical_form optional
        self.fields['medical_form'].required = False
        # Make BECE results optional (will be uploaded later)
        self.fields['bece_results'].required = False
        self.fields['subjects_and_grades'].required = False
        existing_subject_grades = parse_subject_grades(
            self.initial.get('subjects_and_grades')
            or getattr(self.instance, 'subjects_and_grades', '')
        )
        self.subject_grade_fields = []
        for index, subject in enumerate(BECE_SUBJECTS):
            field_name = subject_grade_field_name(index)
            self.fields[field_name] = forms.CharField(
                label=subject,
                required=False,
                initial=existing_subject_grades.get(subject, ''),
                widget=forms.TextInput(attrs={
                    'class': FIELD_CLASS,
                    'inputmode': 'numeric',
                    'pattern': '[0-9]*',
                    'data-numeric-grade': 'true',
                    'aria-label': f'{subject} grade',
                }),
            )
            self.subject_grade_fields.append({
                'subject': subject,
                'field': self[field_name],
            })

    def clean(self):
        cleaned_data = super().clean()
        subject_lines = []

        for index, subject in enumerate(BECE_SUBJECTS):
            field_name = subject_grade_field_name(index)
            grade = str(cleaned_data.get(field_name) or '').strip()
            if grade and not grade.isdigit():
                self.add_error(field_name, 'Enter numbers only.')
                continue
            if grade:
                subject_lines.append(f'{subject}: {grade}')

        cleaned_data['subjects_and_grades'] = '\n'.join(subject_lines)
        return cleaned_data
