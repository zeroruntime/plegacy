from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseForbidden

from accounts.models import CustomUser
from .models import AdmissionRecord
from .forms import AdmissionRecordForm
from .utils.excel_export import export_to_excel, export_summary_to_excel


def check_ownership(user, admission):
    """
    Check if user owns the admission record or is an admin.
    Returns True if user has permission to edit/delete the record.
    """
    return admission.submitted_by == user or user.role == 'admin'


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
            'total_presidents': CustomUser.objects.filter(
                role='president'
            ).count(),
        }
    else:
        context = {
            'page_title': f'{user.year_group} Dashboard',
            'total_records': AdmissionRecord.objects.filter(
                submitted_by=user
            ).count(),
            'year_group': user.year_group,
        }

    return render(request, 'admissions/dashboard.html', context)


@login_required(login_url='accounts:login')
def admission_list(request):
    """
    Display list of admission records.
    Admins see all records, presidents see records from their year group.
    Includes search and filtering.
    """
    user = request.user
    
    # Filter by user role
    if user.role == 'admin':
        records = AdmissionRecord.objects.all()
    else:
        records = AdmissionRecord.objects.filter(submitted_by__year_group=user.year_group)
    
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
    
    # Get unique year groups for dropdown (only for admins)
    year_groups = []
    year_group_filter = request.GET.get('year_group', '')
    if user.role == 'admin':
        # Get all unique year groups from admissions
        year_groups = list(
            AdmissionRecord.objects.all()
            .values_list('submitted_by__year_group', flat=True)
            .distinct()
            .order_by('submitted_by__year_group')
        )
    
    # Filter by year group (only applicable for admins)
    if year_group_filter and user.role == 'admin':
        records = records.filter(submitted_by__year_group=year_group_filter)
    
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
        'year_groups': year_groups,
        'year_group_filter': year_group_filter,
        'is_admin': user.role == 'admin',
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
    if request.method == 'POST':
        form = AdmissionRecordForm(request.POST, request.FILES)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.submitted_by = request.user
            admission.save()
            messages.success(request, f'Admission record for {admission.full_name} created successfully!')
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
    Only allow access if user owns the record or is admin.
    """
    admission = get_object_or_404(AdmissionRecord, pk=pk)
    
    # Check permission
    if not check_ownership(request.user, admission):
        messages.error(request, 'You do not have permission to view this record.')
        return redirect('admissions:admission_list')
    
    context = {
        'page_title': f'Admission - {admission.full_name}',
        'admission': admission,
        'can_edit': check_ownership(request.user, admission),
    }
    return render(request, 'admissions/admission_detail.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(['GET', 'POST'])
def admission_edit(request, pk):
    """
    Edit an admission record.
    GET: Display pre-filled form
    POST: Save changes
    Only allow editing by user who created the record or admin.
    """
    admission = get_object_or_404(AdmissionRecord, pk=pk)
    
    # Check permission
    if not check_ownership(request.user, admission):
        messages.error(request, 'You do not have permission to edit this record.')
        return redirect('admissions:admission_list')
    
    if request.method == 'POST':
        form = AdmissionRecordForm(request.POST, request.FILES, instance=admission)
        if form.is_valid():
            form.save()
            messages.success(request, f'Admission record for {admission.full_name} updated successfully!')
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
    Only allow deletion by user who created the record or admin.
    """
    admission = get_object_or_404(AdmissionRecord, pk=pk)
    
    # Check permission
    if not check_ownership(request.user, admission):
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
def export_detailed_excel(request):
    """
    Export all admission records to detailed Excel file with images.
    Admin-only access.
    """
    # Check if user is admin
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to export records.')
        return HttpResponseForbidden('Access denied. Admin only.')
    
    # Get all records
    queryset = AdmissionRecord.objects.all()
    
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
    
    # Get all records
    queryset = AdmissionRecord.objects.all()
    
    # Generate and return Excel file
    return export_summary_to_excel(queryset)
