from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseForbidden
from django.utils import timezone

from accounts.models import CustomUser
from .models import AdmissionRecord
from .forms import AdmissionRecordForm
from .utils.excel_export import export_to_excel, export_summary_to_excel
from .utils.validation_routing import get_validation_recipient


def check_view_permission(user, admission):
    """
    Check if a user can view an admission record.
    """
    if user.role == 'admin':
        return True
    if admission.submitted_by == user:
        return True
    return user.role == 'president' and admission.alumni_year_group == user.year_group


def check_edit_permission(user, admission):
    """
    Individuals can revise their own non-approved submissions.
    Admins retain full edit access.
    """
    if user.role == 'admin':
        return True
    return admission.submitted_by == user and admission.validation_status != 'approved'


def check_validation_permission(user, admission):
    """
    Presidents validate records from their year group; admins may also validate.
    """
    if user.role == 'admin':
        return True
    return user.role == 'president' and admission.alumni_year_group == user.year_group


def update_completion_status(admission):
    admission.status = 'complete' if admission.bece_results else 'incomplete'


def add_validation_routing_message(request, admission):
    recipient = get_validation_recipient(admission.alumni_year_group)
    if recipient:
        messages.success(
            request,
            f'Admission record for {admission.full_name} submitted for validation by the {admission.alumni_year_group} year group president.'
        )
        return

    messages.error(
        request,
        f'Admission record for {admission.full_name} was saved, but no active president account is configured for {admission.alumni_year_group}.'
    )


@login_required
def dashboard(request):
    """
    Display dashboard with overview and quick stats.
    """
    user = request.user

    if user.is_admin():
        context = {
            'page_title': 'Admin Dashboard',
            'total_records': AdmissionRecord.objects.count(),
            'approved_records': AdmissionRecord.objects.filter(
                validation_status='approved'
            ).count(),
            'pending_records': AdmissionRecord.objects.filter(
                validation_status='pending'
            ).count(),
            'total_presidents': CustomUser.objects.filter(
                role='president'
            ).count(),
        }
    elif user.is_president():
        records = AdmissionRecord.objects.filter(alumni_year_group=user.year_group)
        context = {
            'page_title': f'{user.year_group} Dashboard',
            'total_records': records.count(),
            'pending_records': records.filter(validation_status='pending').count(),
            'approved_records': records.filter(validation_status='approved').count(),
            'year_group': user.year_group,
        }
    else:
        records = AdmissionRecord.objects.filter(submitted_by=user)
        context = {
            'page_title': 'My Admissions Dashboard',
            'total_records': records.count(),
            'pending_records': records.filter(validation_status='pending').count(),
            'approved_records': records.filter(validation_status='approved').count(),
            'year_group': user.year_group,
        }

    return render(request, 'admissions/dashboard.html', context)


@login_required(login_url='accounts:login')
def admission_list(request):
    """
    Display list of admission records.
    Admins see all records, presidents see records from their year group,
    and individuals see records they submitted themselves.
    Includes search and filtering.
    """
    user = request.user
    
    # Filter by user role
    if user.role == 'admin':
        records = AdmissionRecord.objects.all()
    elif user.role == 'president':
        records = AdmissionRecord.objects.filter(alumni_year_group=user.year_group)
    else:
        records = AdmissionRecord.objects.filter(submitted_by=user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        records = records.filter(
            Q(full_name__icontains=search_query) |
            Q(program_applied_for__icontains=search_query) |
            Q(alumni_name__icontains=search_query)
        )
    
    # Filter by program
    program_filter = request.GET.get('program', '')
    if program_filter:
        records = records.filter(program_applied_for__icontains=program_filter)
    
    # Filter by accommodation status
    accommodation_filter = request.GET.get('accommodation', '')
    if accommodation_filter:
        records = records.filter(accommodation_status=accommodation_filter)

    validation_filter = request.GET.get('validation_status', '')
    if validation_filter:
        records = records.filter(validation_status=validation_filter)
    
    # Get unique year groups for dropdown (only for admins)
    year_groups = []
    year_group_filter = request.GET.get('year_group', '')
    if user.role == 'admin':
        # Get all unique year groups from admissions
        year_groups = list(
            AdmissionRecord.objects.all()
            .values_list('alumni_year_group', flat=True)
            .distinct()
            .order_by('alumni_year_group')
        )
    
    # Filter by year group (only applicable for admins)
    if year_group_filter and user.role == 'admin':
        records = records.filter(alumni_year_group=year_group_filter)
    
    # Pagination
    paginator = Paginator(records, 20)  # Show 20 records per page
    page = request.GET.get('page')
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)
    
    context = {
        'page_title': 'Admission Records',
        'records': records,
        'search_query': search_query,
        'program_filter': program_filter,
        'accommodation_filter': accommodation_filter,
        'validation_filter': validation_filter,
        'year_groups': year_groups,
        'year_group_filter': year_group_filter,
        'is_admin': user.role == 'admin',
        'is_president': user.role == 'president',
    }
    return render(request, 'admissions/admission_list.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(['GET', 'POST'])
def admission_create(request):
    """
    Create a new admission record.
    GET: Display empty form
    POST: Save the admission record with submitted_by set to current user
    """
    if request.user.is_president():
        messages.error(request, 'Year group presidents validate submissions instead of creating them.')
        return redirect('admissions:admission_list')

    if request.method == 'POST':
        form = AdmissionRecordForm(request.POST, request.FILES)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.submitted_by = request.user
            update_completion_status(admission)
            admission.save()
            add_validation_routing_message(request, admission)
            return redirect('admissions:admission_detail', pk=admission.pk)
    else:
        form = AdmissionRecordForm()
    
    context = {
        'page_title': 'Add Admission Record',
        'form': form,
        'is_create': True,
    }
    return render(request, 'admissions/admission_form.html', context)


@login_required(login_url='accounts:login')
def admission_detail(request, pk):
    """
    Display detailed view of an admission record.
    Only allow access if user is the submitter, the matching president, or admin.
    """
    admission = get_object_or_404(AdmissionRecord, pk=pk)
    
    # Check permission
    if not check_view_permission(request.user, admission):
        messages.error(request, 'You do not have permission to view this record.')
        return redirect('admissions:admission_list')
    
    context = {
        'page_title': f'Admission - {admission.full_name}',
        'admission': admission,
        'can_edit': check_edit_permission(request.user, admission),
        'can_validate': check_validation_permission(request.user, admission),
    }
    return render(request, 'admissions/admission_detail.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(['GET', 'POST'])
def admission_edit(request, pk):
    """
    Edit an admission record.
    GET: Display pre-filled form
    POST: Save changes
    Only allow editing by the submitter while not approved, or admin.
    """
    admission = get_object_or_404(AdmissionRecord, pk=pk)
    
    # Check permission
    if not check_edit_permission(request.user, admission):
        messages.error(request, 'You do not have permission to edit this record.')
        return redirect('admissions:admission_list')
    
    if request.method == 'POST':
        form = AdmissionRecordForm(request.POST, request.FILES, instance=admission)
        if form.is_valid():
            updated_admission = form.save(commit=False)
            update_completion_status(updated_admission)
            if request.user.role != 'admin':
                updated_admission.validation_status = 'pending'
                updated_admission.validated_by = None
                updated_admission.validated_at = None
            updated_admission.save()
            add_validation_routing_message(request, updated_admission)
            return redirect('admissions:admission_detail', pk=admission.pk)
    else:
        form = AdmissionRecordForm(instance=admission)
    
    context = {
        'page_title': f'Edit Admission - {admission.full_name}',
        'form': form,
        'admission': admission,
        'is_create': False,
    }
    return render(request, 'admissions/admission_form.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(['GET', 'POST'])
def admission_delete(request, pk):
    """
    Delete an admission record.
    GET: Display confirmation page
    POST: Delete the record
    Only allow deletion by the submitter while not approved, or admin.
    """
    admission = get_object_or_404(AdmissionRecord, pk=pk)
    
    # Check permission
    if not check_edit_permission(request.user, admission):
        messages.error(request, 'You do not have permission to delete this record.')
        return redirect('admissions:admission_list')
    
    if request.method == 'POST':
        applicant_name = admission.full_name
        admission.delete()
        messages.success(request, f'Admission record for {applicant_name} has been deleted.')
        return redirect('admissions:admission_list')
    
    context = {
        'page_title': f'Delete Admission - {admission.full_name}',
        'admission': admission,
    }
    return render(request, 'admissions/admission_confirm_delete.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(['POST'])
def admission_validate(request, pk):
    """
    Approve or return a record for revision.
    Presidents can validate records from their year group; admins can validate any record.
    """
    admission = get_object_or_404(AdmissionRecord, pk=pk)

    if not check_validation_permission(request.user, admission):
        messages.error(request, 'You do not have permission to validate this record.')
        return redirect('admissions:admission_list')

    action = request.POST.get('action')
    notes = request.POST.get('validation_notes', '').strip()

    if action == 'approve':
        if admission.status != 'complete':
            messages.error(request, 'This record cannot be approved until the BECE results are uploaded.')
            return redirect('admissions:admission_detail', pk=admission.pk)
        admission.validation_status = 'approved'
        success_message = f'Admission record for {admission.full_name} approved.'
    elif action == 'reject':
        admission.validation_status = 'rejected'
        success_message = f'Admission record for {admission.full_name} returned for revision.'
    else:
        messages.error(request, 'Invalid validation action.')
        return redirect('admissions:admission_detail', pk=admission.pk)

    admission.validation_notes = notes
    admission.validated_by = request.user
    admission.validated_at = timezone.now()
    admission.save(update_fields=[
        'validation_status',
        'validation_notes',
        'validated_by',
        'validated_at',
    ])
    messages.success(request, success_message)
    return redirect('admissions:admission_detail', pk=admission.pk)


@login_required(login_url='accounts:login')
def export_detailed_excel(request):
    """
    Export all admission records to detailed Excel file with images.
    Admin-only access.
    """
    # Check if user is admin
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to export records.')
        return HttpResponseForbidden('Access denied. Admin only.')
    
    queryset = AdmissionRecord.objects.filter(validation_status='approved')
    
    # Generate and return Excel file
    return export_to_excel(queryset)


@login_required(login_url='accounts:login')
def export_summary_excel(request):
    """
    Export all admission records to summary Excel file.
    Admin-only access.
    """
    # Check if user is admin
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to export records.')
        return HttpResponseForbidden('Access denied. Admin only.')
    
    queryset = AdmissionRecord.objects.filter(validation_status='approved')
    
    # Generate and return Excel file
    return export_summary_to_excel(queryset)
