from django.db import models
from django.conf import settings
from django.utils import timezone


class AdmissionRecord(models.Model):
    """
    Admission recommendation record submitted by PRESEC alumni.
    Tracks all application information as per the PDF form.
    """
    
    # Gender choices
    GENDER_CHOICES = [
        ('Male', 'Male'),
    ]
    
    # Accommodation choices
    ACCOMMODATION_CHOICES = [
        ('Boarding', 'Boarding'),
        ('Day', 'Day'),
    ]
    
    # ============ APPLICANT DETAILS ============
    full_name = models.CharField(
        max_length=255,
        help_text="Full name of applicant"
    )
    date_of_birth = models.DateField(
        help_text="Applicant's date of birth (DD/MM/YYYY)"
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        help_text="Gender of applicant"
    )
    nationality = models.CharField(
        max_length=100,
        help_text="Applicant's nationality"
    )
    previous_school = models.CharField(
        max_length=255,
        help_text="Previous basic school attended"
    )
    class_completed = models.CharField(
        max_length=50,
        help_text="Class completed (e.g., JHS 3, Primary 6)"
    )
    
    # ============ BECE INFORMATION ============
    bece_index_number = models.CharField(
        max_length=50,
        help_text="BECE Index Number"
    )
    bece_year = models.IntegerField(
        help_text="Year BECE was taken"
    )
    aggregate_score = models.CharField(
        max_length=50,
        help_text="Aggregate score from BECE"
    )
    subjects_and_grades = models.TextField(
        help_text="Subjects and grades (English, Math, Science, Social Studies, Others)"
    )
    
    # ============ PROGRAM & ACCOMMODATION ============
    program_applied_for = models.CharField(
        max_length=100,
        help_text="Program applied for (General Science, Business, etc.)"
    )
    accommodation_status = models.CharField(
        max_length=20,
        choices=ACCOMMODATION_CHOICES,
        help_text="Boarding or Day student"
    )
    
    # ============ PARENT/GUARDIAN INFORMATION ============
    parent_name = models.CharField(
        max_length=255,
        help_text="Full name of parent/guardian"
    )
    parent_relationship = models.CharField(
        max_length=50,
        help_text="Relationship to applicant (Parent, Guardian, etc.)"
    )
    parent_occupation = models.CharField(
        max_length=100,
        help_text="Parent/guardian's occupation"
    )
    parent_contact = models.CharField(
        max_length=20,
        help_text="Parent/guardian's contact number(s)"
    )
    parent_address = models.TextField(
        help_text="Residential address of parent/guardian"
    )
    parent_email = models.EmailField(
        help_text="Email address of parent/guardian"
    )
    
    # ============ ALUMNI SPONSORSHIP/ENDORSEMENT DETAILS ============
    alumni_name = models.CharField(
        max_length=255,
        help_text="Full name of PRESEC Old Boy"
    )
    alumni_year_group = models.CharField(
        max_length=4,
        help_text="Alumni's year group (e.g., 1998, 2005)"
    )
    alumni_class_stream = models.CharField(
        max_length=100,
        help_text="Alumni's class stream (e.g., Science 2, Business 1)"
    )
    alumni_house = models.CharField(
        max_length=100,
        help_text="Alumni's house at PRESEC"
    )
    alumni_phone = models.CharField(
        max_length=20,
        help_text="Alumni's phone number"
    )
    alumni_email = models.EmailField(
        help_text="Alumni's email address"
    )
    alumni_occupation = models.CharField(
        max_length=100,
        help_text="Alumni's current occupation/title"
    )
    alumni_organization = models.CharField(
        max_length=255,
        help_text="Alumni's current organization/institution"
    )
    alumni_relationship = models.CharField(
        max_length=100,
        help_text="Alumni's relationship to applicant"
    )
    reason_for_recommendation = models.TextField(
        help_text="Reason for recommendation by alumnus"
    )
    
    # ============ FILE ATTACHMENTS ============
    bece_results = models.FileField(
        upload_to='attachments/bece_results/',
        help_text="Copy of BECE Results Slip"
    )
    passport_photo = models.ImageField(
        upload_to='attachments/passport_photos/',
        help_text="Passport photograph"
    )
    birth_certificate = models.FileField(
        upload_to='attachments/birth_certificates/',
        help_text="Birth certificate"
    )
    medical_form = models.FileField(
        upload_to='attachments/medical_forms/',
        blank=True,
        null=True,
        help_text="Medical form (optional)"
    )
    
    # ============ ADMINISTRATIVE FIELDS ============
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admission_records',
        help_text="User who submitted this admission record"
    )
    date_submitted = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the record was submitted"
    )
    
    class Meta:
        ordering = ['-date_submitted']
        verbose_name = 'Admission Record'
        verbose_name_plural = 'Admission Records'
        indexes = [
            models.Index(fields=['submitted_by', '-date_submitted']),
            models.Index(fields=['full_name']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.program_applied_for} ({self.date_submitted.year})"
    
    def get_applicant_info(self):
        """Return a dict of applicant information for template display."""
        return {
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'nationality': self.nationality,
            'previous_school': self.previous_school,
            'class_completed': self.class_completed,
        }
    
    def get_bece_info(self):
        """Return a dict of BECE information for template display."""
        return {
            'bece_index_number': self.bece_index_number,
            'bece_year': self.bece_year,
            'aggregate_score': self.aggregate_score,
            'subjects_and_grades': self.subjects_and_grades,
        }
    
    def get_alumni_info(self):
        """Return a dict of alumni information for template display."""
        return {
            'alumni_name': self.alumni_name,
            'alumni_year_group': self.alumni_year_group,
            'alumni_class_stream': self.alumni_class_stream,
            'alumni_house': self.alumni_house,
            'alumni_phone': self.alumni_phone,
            'alumni_email': self.alumni_email,
        }
