from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from .choices import BECE_SUBJECTS
from .models import AdmissionRecord
from .forms import AdmissionRecordForm, subject_grade_field_name
from .utils.aggregate_score import AggregateScoreError, calculate_aggregate_score


class AggregateScoreTests(TestCase):
    def test_calculates_best_four_core_and_best_two_electives(self):
        result = calculate_aggregate_score({
            'ENGLISH LANGUAGE': '2',
            'MATHEMATICS': '1',
            'SCIENCE': '3',
            'SOCIAL STUDIES': '4',
            'ARABIC': '6',
            'COMPUTING': '2',
            'FRENCH': '1',
        })

        self.assertEqual(result['score'], 13)
        self.assertEqual(result['subjects'], [
            ('MATHEMATICS', 1),
            ('ENGLISH LANGUAGE', 2),
            ('SCIENCE', 3),
            ('SOCIAL STUDIES', 4),
            ('FRENCH', 1),
            ('COMPUTING', 2),
        ])

    def test_ignores_zero_grades(self):
        result = calculate_aggregate_score({
            'ENGLISH LANGUAGE': '1',
            'MATHEMATICS': '1',
            'SCIENCE': '2',
            'SOCIAL STUDIES': '2',
            'ARABIC': '0',
            'COMPUTING': '3',
            'FRENCH': '4',
        })

        self.assertEqual(result['score'], 13)
        self.assertEqual(result['subjects'][-2:], [('COMPUTING', 3), ('FRENCH', 4)])

    def test_rejects_missing_core_subjects(self):
        with self.assertRaisesMessage(AggregateScoreError, 'Enter valid grades for all 4 core subjects'):
            calculate_aggregate_score({
                'ENGLISH LANGUAGE': '1',
                'MATHEMATICS': '1',
                'SCIENCE': '0',
                'SOCIAL STUDIES': '2',
                'COMPUTING': '3',
                'FRENCH': '4',
            })


class AdmissionRecordFormTests(TestCase):
    def form_data(self, grade_overrides=None):
        grades = {
            'ARABIC': '6',
            'CAREER TECHNOLOGY': '5',
            'COMPUTING': '2',
            'CREATIVE ART AND DESIGN': '0',
            'ENGLISH LANGUAGE': '2',
            'FRENCH': '1',
            'GHANAIAN LANGUAGE': '0',
            'MATHEMATICS': '1',
            'RELIGIOUS AND MORAL EDUCATION': '0',
            'SCIENCE': '3',
            'SOCIAL STUDIES': '4',
        }
        grades.update(grade_overrides or {})

        data = {
            'full_name': 'Test Applicant',
            'date_of_birth': '2012-01-01',
            'gender': 'Male',
            'nationality': 'Ghanaian',
            'previous_school': 'Test JHS',
            'class_completed': 'JHS 3',
            'bece_index_number': '1234567890',
            'bece_year': '2025',
            'aggregate_score': '99',
            'program_applied_for': 'General Science',
            'accommodation_status': 'Boarding',
            'parent_name': 'Test Parent',
            'parent_relationship': 'Parent',
            'parent_occupation': 'Teacher',
            'parent_contact': '0240000000',
            'parent_address': 'Accra',
            'parent_email': 'parent@example.com',
            'alumni_name': 'Test Alumnus',
            'alumni_year_group': '2000',
            'alumni_class_stream': 'Science 1',
            'alumni_house': 'House 1',
            'alumni_phone': '0241111111',
            'alumni_email': 'alumnus@example.com',
            'alumni_occupation': 'Engineer',
            'alumni_organization': 'Example Ltd',
            'alumni_relationship': 'Son',
            'reason_for_recommendation': 'Recommended applicant.',
        }

        for index, subject in enumerate(BECE_SUBJECTS):
            data[subject_grade_field_name(index)] = grades[subject]

        return data

    def form_files(self):
        image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )
        return {
            'passport_photo': SimpleUploadedFile('photo.gif', image, content_type='image/gif'),
            'birth_certificate': SimpleUploadedFile('birth.pdf', b'%PDF-1.4\n', content_type='application/pdf'),
        }

    def test_form_calculates_aggregate_and_forces_bece_year(self):
        form = AdmissionRecordForm(data=self.form_data(), files=self.form_files())

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['bece_year'], 2026)
        self.assertEqual(form.cleaned_data['aggregate_score'], '13')
        self.assertIn('SCIENCE: 3', form.cleaned_data['subjects_and_grades'])
        admission = form.save(commit=False)
        self.assertEqual(admission.bece_year, 2026)
        self.assertEqual(admission.aggregate_score, '13')

    def test_form_rejects_invalid_grade_range(self):
        form = AdmissionRecordForm(
            data=self.form_data({'SCIENCE': '10'}),
            files=self.form_files(),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('subjects_and_grades', form.errors)
        self.assertIn('SCIENCE grade must be between 0 and 9.', form.errors['subjects_and_grades'])

    def test_form_rejects_insufficient_elective_grades(self):
        form = AdmissionRecordForm(
            data=self.form_data({
                'ARABIC': '0',
                'CAREER TECHNOLOGY': '0',
                'COMPUTING': '0',
                'FRENCH': '0',
            }),
            files=self.form_files(),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('Enter valid grades for at least 2 elective subjects.', form.errors['subjects_and_grades'])


class AdmissionWorkflowRedirectTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='individual',
            password='password',
            role='individual',
            year_group='2000',
        )
        self.president = CustomUser.objects.create_user(
            username='president',
            password='password',
            role='president',
            year_group='2000',
        )

    def form_data(self):
        return AdmissionRecordFormTests().form_data()

    def form_files(self):
        return AdmissionRecordFormTests().form_files()

    def admission(self):
        return AdmissionRecord.objects.create(
            full_name='Test Applicant',
            date_of_birth='2012-01-01',
            gender='Male',
            nationality='Ghanaian',
            previous_school='Test JHS',
            class_completed='JHS 3',
            bece_index_number='1234567890',
            bece_year=2026,
            aggregate_score='13',
            subjects_and_grades='ENGLISH LANGUAGE: 2\nMATHEMATICS: 1\nSCIENCE: 3\nSOCIAL STUDIES: 4\nFRENCH: 1\nCOMPUTING: 2',
            program_applied_for='General Science',
            accommodation_status='Boarding',
            parent_name='Test Parent',
            parent_relationship='Parent',
            parent_occupation='Teacher',
            parent_contact='0240000000',
            parent_address='Accra',
            parent_email='parent@example.com',
            alumni_name='Test Alumnus',
            alumni_year_group='2000',
            alumni_class_stream='Science 1',
            alumni_house='House 1',
            alumni_phone='0241111111',
            alumni_email='alumnus@example.com',
            alumni_occupation='Engineer',
            alumni_organization='Example Ltd',
            alumni_relationship='Son',
            reason_for_recommendation='Recommended applicant.',
            submitted_by=self.user,
            status='complete',
            validation_status='pending',
        )

    def test_create_redirects_to_records_list(self):
        self.client.force_login(self.user)
        data = self.form_data()
        data.update(self.form_files())

        response = self.client.post(
            reverse('admissions:admission_create'),
            data=data,
        )

        self.assertRedirects(response, reverse('admissions:admission_list'))

    def test_edit_redirects_to_records_list(self):
        admission = self.admission()
        self.client.force_login(self.user)
        data = self.form_data()
        data.update(self.form_files())

        response = self.client.post(
            reverse('admissions:admission_edit', kwargs={'pk': admission.pk}),
            data=data,
        )

        self.assertRedirects(response, reverse('admissions:admission_list'))

    def test_validation_redirects_to_records_list(self):
        admission = self.admission()
        self.client.force_login(self.president)

        response = self.client.post(
            reverse('admissions:admission_validate', kwargs={'pk': admission.pk}),
            data={'action': 'approve'},
        )

        self.assertRedirects(response, reverse('admissions:admission_list'))
