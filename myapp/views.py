import csv, os, zipfile, io,  tempfile
import pandas as pd
from io import StringIO
from io import BytesIO
from django.core.files import File
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from datetime import timedelta
from itertools import chain
from operator import attrgetter
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from .models import Admin, MayorsPermit, IDCard, Mtop, Franchise, MayorsPermitTricycle, SuperAdmin, AdminPermission,MayorsPermitHistory, MayorsPermitTricycleHistory,ActivityLog
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from .forms import CSVUploadForm
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_http_methods, require_POST
from functools import wraps
import logging
from django.utils.timezone import now
from django.conf import settings
from django.db import transaction
import shutil
import openpyxl
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.serializers import serialize
from django.utils.timezone import localtime


def superadmin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_type') != 'superadmin':
            messages.error(request, 'Access denied. Only Super Admins can access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

@require_http_methods(["POST"])


def update_permit_tri(request, permit_id):
    # Only allow POST requests
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        }, status=405)
    
    try:
        permit = get_object_or_404(MayorsPermitTricycle, id=permit_id)

        data = json.loads(request.body)

        # ✅ Save previous status BEFORE updating
        previous_status = permit.status
        new_status = data.get('status')

        # -------- Update fields --------
        permit.control_no = data.get('control_no')
        permit.name = data.get('name')
        permit.address = data.get('address')
        permit.motorized_operation = data.get('motorized_operation')
        permit.business_name = data.get('business_name')

        if data.get('issue_date'):
            permit.issue_date = datetime.strptime(
                data.get('issue_date'), '%Y-%m-%d'
            ).date()

        if data.get('expiry_date'):
            permit.expiry_date = datetime.strptime(
                data.get('expiry_date'), '%Y-%m-%d'
            ).date()

        permit.amount_paid = int(data.get('amount_paid', 0))
        permit.or_no = data.get('or_no')
        permit.issued_at = data.get('issued_at')
        permit.mayor = data.get('mayor')
        permit.quarter = data.get('quarter')
        permit.status = new_status

        permit.save()

        # -------- ✅ CREATE HISTORY WITH USER INFO IF STATUS CHANGED --------
        if previous_status != new_status:
            # Get user info from session
            user_type = request.session.get('user_type')
            user_id = request.session.get('superadmin_id') if user_type == 'superadmin' else request.session.get('admin_id')
            user_name = request.session.get('full_name')
            
            MayorsPermitTricycleHistory.objects.create(
                permit=permit,
                previous_status=previous_status,
                new_status=new_status,
                remarks=f"Status changed from {previous_status} to {new_status}",
                updated_by_type=user_type,
                updated_by_id=user_id,
                updated_by_name=user_name
            )

        messages.success(request, f'Permit for {permit.name} updated successfully!')

        return JsonResponse({
            'success': True,
            'message': 'Permit updated successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    

@require_POST
def add_mtop(request):

    case_no = request.POST.get("case_no")
    motor_no = request.POST.get("motor_no")
    chasses_no = request.POST.get("chasses_no")

    # ✅ FIELD-LEVEL VALIDATION
    if Mtop.objects.filter(case_no=case_no).exists():
        messages.error(request, f"Case No '{case_no}' already exists.")
        return JsonResponse({"success": False})

    if Mtop.objects.filter(motor_no=motor_no).exists():
        messages.error(request, f"Motor No '{motor_no}' already exists.")
        return JsonResponse({"success": False})

    if Mtop.objects.filter(chasses_no=chasses_no).exists():
        messages.error(request, f"Chassis No '{chasses_no}' already exists.")
        return JsonResponse({"success": False})

    try:
        mtop = Mtop.objects.create(
            name=request.POST.get("name"),
            case_no=case_no,
            address=request.POST.get("address"),
            no_of_units=request.POST.get("no_of_units"),
            route_operation=request.POST.get("route_operation"),
            make=request.POST.get("make"),
            motor_no=motor_no,
            chasses_no=chasses_no,
            plate_no=request.POST.get("plate_no"),
            date=request.POST.get("date"),
            municipal_treasurer=request.POST.get("municipal_treasurer"),
            officer_in_charge=request.POST.get("officer_in_charge"),
            mayor=request.POST.get("mayor"),
        )

        messages.success(request, f"{mtop.name} successfully added.")
        return JsonResponse({"success": True})

    except Exception as e:
        messages.error(request, "An unexpected error occurred while saving the record.")
        return JsonResponse({"success": False})



# New view to add franchise
@require_http_methods(["POST"])
def add_franchise(request):
    try:
        # Get data from POST request
        name = request.POST.get('name')
        denomination = request.POST.get('denomination')
        plate_no = request.POST.get('plate_no')
        valid_until = request.POST.get('valid_until')
        motor_no = request.POST.get('motor_no')
        authorized_no = request.POST.get('authorized_no')
        chassis_no = request.POST.get('chassis_no')
        authorized_route = request.POST.get('authorized_route')
        purpose = request.POST.get('purpose')
        official_receipt_no = request.POST.get('official_receipt_no')
        date = request.POST.get('date')
        amount_paid = request.POST.get('amount_paid')
        municipal_treasurer = request.POST.get('municipal_treasurer')


        # Check for duplicate Plate Number
        if Franchise.objects.filter(plate_no=plate_no).exists():
            messages.error(request, f'Plate Number "{plate_no}" already exists!')
            return JsonResponse({
                'success': False,
                'message': f'Plate Number "{plate_no}" already exists!'
            }, status=400)

        # Check for duplicate Authorized Number
        if Franchise.objects.filter(authorized_no=authorized_no).exists():
            messages.error(request, f'Authorized Number "{authorized_no}" already exists!')
            return JsonResponse({
                'success': False,
                'message': f'Authorized Number "{authorized_no}" already exists!'
            }, status=400)


        # Create new Franchise record
        franchise = Franchise.objects.create(
            name=name,
            denomination=denomination,
            plate_no=plate_no,
            valid_until=valid_until,
            motor_no=motor_no,
            authorized_no=authorized_no,
            chassis_no=chassis_no,
            authorized_route=authorized_route,
            purpose=purpose,
            official_receipt_no=official_receipt_no,
            date=date,
            amount_paid=amount_paid,
            municipal_treasurer=municipal_treasurer
        )

        # Add success message
        messages.success(request, f'Franchise record for {name} added successfully!')

        return JsonResponse({
            'success': True,
            'message': 'Franchise record added successfully!',
            'id': franchise.id
        })

    except Exception as e:
        # Add error message
        messages.error(request, f'Error adding franchise record: {str(e)}')
        
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)



@require_http_methods(["POST"])
def update_franchise(request):
    try:
        # Get the franchise ID
        franchise_id = request.POST.get('id')
        
        # Get the franchise object
        franchise = Franchise.objects.get(id=franchise_id)
        
        # Get data from POST request
        plate_no = request.POST.get('plate_no')
        authorized_no = request.POST.get('authorized_no')
        
        # Check for duplicate Plate Number (excluding current record)
        if Franchise.objects.filter(plate_no=plate_no).exclude(id=franchise_id).exists():
            messages.error(request, f'Plate Number "{plate_no}" already exists!')
            return JsonResponse({
                'success': False,
                'message': f'Plate Number "{plate_no}" already exists!'
            }, status=400)

        # Check for duplicate Authorized Number (excluding current record)
        if Franchise.objects.filter(authorized_no=authorized_no).exclude(id=franchise_id).exists():
            messages.error(request, f'Authorized Number "{authorized_no}" already exists!')
            return JsonResponse({
                'success': False,
                'message': f'Authorized Number "{authorized_no}" already exists!'
            }, status=400)

        # Update franchise record
        franchise.name = request.POST.get('name')
        franchise.denomination = request.POST.get('denomination')
        franchise.plate_no = plate_no
        franchise.valid_until = request.POST.get('valid_until')
        franchise.motor_no = request.POST.get('motor_no')
        franchise.authorized_no = authorized_no
        franchise.chassis_no = request.POST.get('chassis_no')
        franchise.authorized_route = request.POST.get('authorized_route')
        franchise.purpose = request.POST.get('purpose')
        franchise.official_receipt_no = request.POST.get('official_receipt_no')
        franchise.date = request.POST.get('date')
        franchise.amount_paid = request.POST.get('amount_paid')
        franchise.municipal_treasurer = request.POST.get('municipal_treasurer')
        
        franchise.save()

        # Add success message
        messages.success(request, f'Franchise record for {franchise.name} updated successfully!')

        return JsonResponse({
            'success': True,
            'message': 'Franchise record updated successfully!',
            'id': franchise.id
        })

    except Franchise.DoesNotExist:
        messages.error(request, 'Franchise record not found!')
        return JsonResponse({
            'success': False,
            'message': 'Franchise record not found!'
        }, status=404)

    except Exception as e:
        # Add error message
        messages.error(request, f'Error updating franchise record: {str(e)}')
        
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    
def get_mtop(request, id):
    mtop = get_object_or_404(Mtop, id=id)

    return JsonResponse({
        "id": mtop.id,
        "name": mtop.name,
        "case_no": mtop.case_no,
        "address": mtop.address,
        "no_of_units": mtop.no_of_units,
        "route_operation": mtop.route_operation,
        "make": mtop.make,
        "motor_no": mtop.motor_no,
        "chasses_no": mtop.chasses_no,
        "plate_no": mtop.plate_no,
        "date": mtop.date.strftime("%Y-%m-%d"),
        "municipal_treasurer": mtop.municipal_treasurer,
        "officer_in_charge": mtop.officer_in_charge,
        "mayor": mtop.mayor,
    })


@require_POST
def update_mtop(request):
    mtop = get_object_or_404(Mtop, id=request.POST.get("id"))

    # UNIQUE FIELD CHECK (exclude self)
    if Mtop.objects.filter(case_no=request.POST["case_no"]).exclude(id=mtop.id).exists():
        messages.error(request, "Case No already exists.")
        return JsonResponse({"success": False})

    if Mtop.objects.filter(motor_no=request.POST["motor_no"]).exclude(id=mtop.id).exists():
        messages.error(request, "Motor No already exists.")
        return JsonResponse({"success": False})

    if Mtop.objects.filter(chasses_no=request.POST["chasses_no"]).exclude(id=mtop.id).exists():
        messages.error(request, "Chassis No already exists.")
        return JsonResponse({"success": False})

    # UPDATE
    mtop.name = request.POST.get("name")
    mtop.case_no = request.POST.get("case_no")
    mtop.address = request.POST.get("address")
    mtop.no_of_units = request.POST.get("no_of_units")
    mtop.route_operation = request.POST.get("route_operation")
    mtop.make = request.POST.get("make")
    mtop.motor_no = request.POST.get("motor_no")
    mtop.chasses_no = request.POST.get("chasses_no")
    mtop.plate_no = request.POST.get("plate_no")
    mtop.date = request.POST.get("date")
    mtop.municipal_treasurer = request.POST.get("municipal_treasurer")
    mtop.officer_in_charge = request.POST.get("officer_in_charge")
    mtop.mayor = request.POST.get("mayor")
    mtop.save()

    messages.success(request, f"{mtop.name} successfully updated.")
    return JsonResponse({"success": True})


def admin_login(request):
    """Handle admin and superadmin login. Redirects to dashboard on success."""

    if request.session.get('admin_id') or request.session.get('superadmin_id'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # First, try SuperAdmin login
        try:
            superadmin = SuperAdmin.objects.get(username=username)
            if check_password(password, superadmin.password) or superadmin.password == password:
                # Store superadmin info in session
                request.session['superadmin_id'] = superadmin.id
                request.session['user_type'] = 'superadmin'
                request.session['username'] = superadmin.username
                request.session['full_name'] = superadmin.full_name
                # Superadmins have access to all sections
                request.session['can_access_potpot_registration'] = True
                request.session['can_access_motorcycle_registration'] = True
                messages.success(request, f'Welcome back, {superadmin.full_name}!')
                return redirect('dashboard')
        except SuperAdmin.DoesNotExist:
            pass

        # If not SuperAdmin, try Admin login
        try:
            admin = Admin.objects.get(username=username)
            if check_password(password, admin.password) or admin.password == password:
                # Store admin info in session
                request.session['admin_id'] = admin.id
                request.session['user_type'] = 'admin'
                request.session['username'] = admin.username
                request.session['full_name'] = admin.full_name
                # Load admin permissions (if any) into session
                try:
                    perms = admin.permissions
                    request.session['can_access_potpot_registration'] = bool(perms.can_access_potpot_registration)
                    request.session['can_access_motorcycle_registration'] = bool(perms.can_access_motorcycle_registration)
                except AdminPermission.DoesNotExist:
                    request.session['can_access_potpot_registration'] = False
                    request.session['can_access_motorcycle_registration'] = False

                messages.success(request, f'Welcome back, {admin.full_name}!')
                return redirect('dashboard')
        except Admin.DoesNotExist:
            pass

        # If we reach here, login failed
        messages.error(request, 'Invalid username or password.')

    content = {'exclude_layout': True}
    return render(request, 'myapp/login.html', content)

def dashboard(request):
    permit_count = MayorsPermit.objects.count()
    tricycle_count = MayorsPermitTricycle.objects.count() 
     
    # Mayor's Permit (Pedicab) - Status counts
    pedicab_active = MayorsPermit.objects.filter(status='active').count()
    pedicab_inactive = MayorsPermit.objects.filter(status='inactive').count()
    pedicab_expired = MayorsPermit.objects.filter(status='expired').count()

    # Mayor's Permit (Tricycle/Motorcycle) - Status counts
    tricycle_active = MayorsPermitTricycle.objects.filter(status='active').count()
    tricycle_inactive = MayorsPermitTricycle.objects.filter(status='inactive').count()
    tricycle_expired = MayorsPermitTricycle.objects.filter(status='expired').count()

   # ============ RECENT ACTIVITIES - Get from ActivityLog ============
    # Filter activities based on user permissions
    user_type = request.session.get('user_type')
    can_potpot = request.session.get('can_access_potpot_registration', False)
    can_motor = request.session.get('can_access_motorcycle_registration', False)

    # Build query based on permissions
    if user_type == 'superadmin':
        # Superadmin sees all activities
        recent_activities_raw = ActivityLog.objects.order_by('-timestamp')[:20]
    else:
        # Admin sees only activities for their permitted models
        allowed_models = []
        if can_potpot:
            allowed_models.extend(['potpot', 'idcard'])
        if can_motor:
            allowed_models.extend(['motorcycle', 'mtop', 'franchise'])
        
        if allowed_models:
            recent_activities_raw = (
                ActivityLog.objects
                .filter(model_type__in=allowed_models)
                .order_by('-timestamp')[:20]
            )
        else:
            recent_activities_raw = ActivityLog.objects.none()
    

    
    recent_activities = []
    for log in recent_activities_raw:
        # Determine icon and color based on action and model
        if log.action == 'create':
            icon = 'fa-plus-circle'
            color = 'success'
        elif log.action == 'update':
            icon = 'fa-edit'
            color = 'info'
        elif log.action == 'delete':
            icon = 'fa-trash'
            color = 'danger'
        elif log.action == 'status_change':
            icon = 'fa-sync'
            color = 'warning'
        else:
            icon = 'fa-info-circle'
            color = 'secondary'
        
        # Format the title based on model type
        model_display = dict(ActivityLog.MODEL_CHOICES).get(log.model_type, log.model_type)
        action_display = dict(ActivityLog.ACTION_CHOICES).get(log.action, log.action)
        
        activity = {
            'type': log.action,
            'model_type': log.model_type,
            'title': f'{model_display} {action_display}',
            'description': log.description,
            'timestamp': log.timestamp,
            'icon': icon,
            'color': color,
            'object_id': log.object_id,
            'updated_by': log.user_name or 'System'
        }
        recent_activities.append(activity)
    
    # Add expiring soon warnings
    expiring_soon_date = timezone.now().date() + timedelta(days=30)
    
    expiring_pedicab = MayorsPermit.objects.filter(
        expiry_date__lte=expiring_soon_date,
        expiry_date__gte=timezone.now().date(),
        status='active'
    ).count()
    
    expiring_tricycle = MayorsPermitTricycle.objects.filter(
        expiry_date__lte=expiring_soon_date,
        expiry_date__gte=timezone.now().date(),
        status='active'
    ).count()
    
    if expiring_pedicab > 0:
        recent_activities.insert(0, {
            'type': 'expiring_soon',
            'model_type': 'potpot',
            'title': 'Potpot Permits Expiring Soon',
            'description': f'{expiring_pedicab} permits expiring in the next 30 days',
            'timestamp': timezone.now(),
            'icon': 'fa-exclamation-triangle',
            'color': 'warning'
        })
    
    if expiring_tricycle > 0:
        recent_activities.insert(0, {
            'type': 'expiring_soon',
            'model_type': 'motorcycle',
            'title': 'Motorcycle Permits Expiring Soon',
            'description': f'{expiring_tricycle} permits expiring in the next 30 days',
            'timestamp': timezone.now(),
            'icon': 'fa-exclamation-triangle',
            'color': 'warning'
        })

    context = {
        'permit_count': permit_count,
        'tricycle_count': tricycle_count,
        'pedicab_active': pedicab_active,
        'pedicab_inactive': pedicab_inactive,
        'pedicab_expired': pedicab_expired,
        'tricycle_active': tricycle_active,
        'tricycle_inactive': tricycle_inactive,
        'tricycle_expired': tricycle_expired,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'myapp/dashboard.html', context)


@superadmin_required
def admin_management(request):
    # REMOVED .prefetch_related('permissions')
    admins = Admin.objects.all().select_related('created_by').order_by('-created_at')
    
    context = {
        'admins': admins,
    }
    return render(request, 'myapp/admin-management.html', context)


@require_POST
@superadmin_required
def add_admin(request):
    super_admin_id = request.session.get('superadmin_id')

    if not super_admin_id:
        messages.error(request, "Unauthorized access.")
        return redirect('admin-management')

    super_admin = SuperAdmin.objects.get(id=super_admin_id)

    username = request.POST.get('username')
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    password = request.POST.get('password')

    # Permissions
    can_access_potpot_registration = request.POST.get('can_access_potpot_registration') == '1'
    can_access_motorcycle_registration = request.POST.get('can_access_motorcycle_registration') == '1'

    if Admin.objects.filter(username=username).exists():
        messages.error(request, "Username already exists.")
        return redirect('admin-management')

    if Admin.objects.filter(email=email).exists():
        messages.error(request, "Email already exists.")
        return redirect('admin-management')

    try:
        # 1️⃣ Create admin
        admin = Admin.objects.create(
            username=username,
            full_name=full_name,
            email=email,
            password=make_password(password),
            created_by=super_admin
        )

        # 2️⃣ Create admin permissions
        AdminPermission.objects.create(
            admin=admin,
            can_access_potpot_registration=can_access_potpot_registration,
            can_access_motorcycle_registration=can_access_motorcycle_registration,
            updated_by=super_admin
        )

        messages.success(request, "Admin created successfully.")

    except Exception as e:
        messages.error(request, f"Error creating admin: {str(e)}")

    return redirect('admin-management')


# @superadmin_required
# def get_admin_details(request, admin_id):
#     """
#     Returns JSON with all admin details including permissions and created_by info
#     """
#     admin = get_object_or_404(Admin.objects.select_related('created_by', 'permissions'), id=admin_id)

#     data = {
#         "id": admin.id,
#         "username": admin.username,
#         "full_name": admin.full_name,
#         "email": admin.email,
#         "is_active": admin.is_active,
#         "created_by": admin.created_by.full_name if admin.created_by else None,
#         "created_at": admin.created_at.strftime("%b %d, %Y"),
#         "permissions": {
#             "can_access_potpot_registration": admin.permissions.can_access_potpot_registration,
#             "can_access_motorcycle_registration": admin.permissions.can_access_motorcycle_registration,
#         }
#     }

#     return JsonResponse(data)


@require_POST
@superadmin_required
def update_admin(request):
    """Handle updates to an Admin and their permissions."""
    super_admin_id = request.session.get('superadmin_id')
    if not super_admin_id:
        messages.error(request, "Unauthorized access.")
        return redirect('admin-management')

    super_admin = SuperAdmin.objects.get(id=super_admin_id)

    admin_id = request.POST.get('admin_id')
    if not admin_id:
        messages.error(request, "Missing admin identifier.")
        return redirect('admin-management')

    admin = get_object_or_404(Admin, id=admin_id)

    username = request.POST.get('username', '').strip()
    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()
    status = request.POST.get('status')
    is_active = True if status == '1' else False

    # Validate uniqueness if changed
    if username and Admin.objects.filter(username=username).exclude(id=admin.id).exists():
        messages.error(request, "Username already exists.")
        return redirect('admin-management')

    if email and Admin.objects.filter(email=email).exclude(id=admin.id).exists():
        messages.error(request, "Email already exists.")
        return redirect('admin-management')

    admin.username = username or admin.username
    admin.full_name = full_name or admin.full_name
    admin.email = email or admin.email
    admin.is_active = is_active

    password = request.POST.get('password', '')
    if password:
        admin.password = make_password(password)

    admin.save()

    # Update or create permissions
    can_potpot = request.POST.get('can_access_potpot_registration') == '1'
    can_moto = request.POST.get('can_access_motorcycle_registration') == '1'

    perm, created = AdminPermission.objects.get_or_create(admin=admin)
    perm.can_access_potpot_registration = can_potpot
    perm.can_access_motorcycle_registration = can_moto
    perm.updated_by = super_admin
    perm.save()

    messages.success(request, "Admin updated successfully.")
    return redirect('admin-management')


def admin_list(request):
   
    return render(request, 'myapp/admin-list.html')

def admin_logout(request):
    """Clear admin and superadmin session and redirect to login."""
    
    # Clear all session keys used in login
    session_keys = ['admin_id', 'superadmin_id', 'user_type', 'username', 'full_name', 'can_access_potpot_registration', 'can_access_motorcycle_registration']
    
    for key in session_keys:
        if key in request.session:
            del request.session[key]
    
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def mayors_permit(request):
    permits = MayorsPermit.objects.all()
    return render(request, 'myapp/mayors-permit.html', {'permits': permits})



def mayors_permit_datatable(request):
    """Server-side processing endpoint for DataTables"""
    
    # DataTables parameters
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Base queryset
    queryset = MayorsPermit.objects.all()
    
    # Global search
    if search_value:
        queryset = queryset.filter(
            Q(control_no__icontains=search_value) |
            Q(name__icontains=search_value) |
            Q(address__icontains=search_value) |
            Q(business_name__icontains=search_value) |
            Q(or_no__icontains=search_value)
        )
    
    # Column-specific search
    for i in range(14):  # 14 columns total
        column_search = request.GET.get(f'columns[{i}][search][value]', '')
        if column_search:
            if i == 0:  # Control No
                queryset = queryset.filter(control_no__icontains=column_search)
            elif i == 1:  # Status - exact match
                queryset = queryset.filter(status__iexact=column_search)
            elif i == 2:  # Name
                queryset = queryset.filter(name__icontains=column_search)
            elif i == 3:  # Address
                queryset = queryset.filter(address__icontains=column_search)
            elif i == 4:  # Business Name
                queryset = queryset.filter(business_name__icontains=column_search)
            elif i == 5:  # Motorized Operation
                queryset = queryset.filter(motorized_operation__icontains=column_search)
            elif i == 6:  # OR No
                queryset = queryset.filter(or_no__icontains=column_search)
            elif i == 7:  # Amount Paid
                queryset = queryset.filter(amount_paid__icontains=column_search)
            elif i == 8:  # Issue Date
                queryset = queryset.filter(issue_date__icontains=column_search)
            elif i == 9:  # Expiry Date
                queryset = queryset.filter(expiry_date__icontains=column_search)
            elif i == 10:  # Issued At
                queryset = queryset.filter(issued_at__icontains=column_search)
            elif i == 11:  # Mayor
                queryset = queryset.filter(mayor__icontains=column_search)
            elif i == 12:  # Quarter
                queryset = queryset.filter(quarter__icontains=column_search)
    
    # Total records
    total_records = MayorsPermit.objects.count()
    filtered_records = queryset.count()
    
    # Pagination
    permits = queryset[start:start + length]
    
    # Format data
    data = []
    for permit in permits:
        # Status badge HTML
        if permit.status == "active":
            status_html = '<span class="badge badge-success">Active</span>'
        elif permit.status == "inactive":
            status_html = '<span class="badge badge-warning">Inactive</span>'
        elif permit.status == "expired":
            status_html = '<span class="badge badge-danger">Expired</span>'
        else:
            status_html = f'<span class="badge badge-secondary">{permit.status.capitalize()}</span>'
        
        # Generate URLs using reverse()
        print_url = reverse('print-mayors-permit', args=[permit.id])
        history_url = reverse('mayors-permit-history', args=[permit.id])
        
      # Action buttons HTML - MODIFIED HISTORY BUTTON
        action_html = f'''
        <div class="btn-group" role="group">
            <a href="#" class="btn btn-sm btn-primary btn-view" data-id="{permit.id}" title="View">
                <i class="fas fa-eye"></i>
            </a>
            <a href="{print_url}" target="_blank" class="btn btn-sm btn-secondary" title="Print">
                <i class="fas fa-print"></i>
            </a>
            <a href="#" class="btn btn-sm btn-info btn-update" data-id="{permit.id}" title="Update">
                <i class="fas fa-edit"></i>
            </a>
            <a href="#" class="btn btn-sm btn-warning btn-history" data-id="{permit.id}" title="Status history">
                <i class="fas fa-history"></i>
            </a>
        </div>
        '''
        
        data.append([
            permit.control_no,
            status_html,
            permit.name,
            permit.address,
            permit.business_name or '',
            permit.motorized_operation or '',
            permit.or_no,
            str(permit.amount_paid),
            permit.issue_date.strftime('%Y-%m-%d'),
            permit.expiry_date.strftime('%Y-%m-%d'),
            permit.issued_at or '',
            permit.mayor or '',
            permit.get_quarter_display(),
            action_html,
            permit.id,  # Hidden column for ID
            permit.status  # Hidden column for raw status value
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })

def get_permit_history(request, permit_id):
    """Get history data for a specific permit"""
    try:
        permit = MayorsPermit.objects.get(id=permit_id)
        
        # Fetch actual history records from database
        history_records = MayorsPermitHistory.objects.filter(permit=permit).order_by('-activated_at')
        
        history_list = []
        for record in history_records:
            history_list.append({
                'date':localtime(record.activated_at).strftime('%Y-%m-%d %I:%M %p'
),
                'old_status': record.previous_status.capitalize(),
                'new_status': record.new_status.capitalize(),
                'changed_by': record.updated_by_name or 'System',
                'reason': record.remarks or ''
            })
        
        history_data = {
            'permit_info': {
                'control_no': permit.control_no,
                'name': permit.name,
                'current_status': permit.status,
            },
            'history': history_list
        }
        
        return JsonResponse({'success': True, 'data': history_data})
        
    except MayorsPermit.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Permit not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
def add_mayors_permit(request):
    if request.method == "POST":
        control_no = request.POST.get("control_no")
        name = request.POST.get("name")
        address = request.POST.get("address")
        motorized_operation = request.POST.get("motorized_operation")
        business_name = request.POST.get("business_name")
        expiry_date = request.POST.get("expiry_date")
        amount_paid = request.POST.get("amount_paid")
        or_no = request.POST.get("or_no")
        issue_date = request.POST.get("issue_date")
        issued_at = request.POST.get("issued_at")
        mayor = request.POST.get("mayor")
        quarter = request.POST.get("quarter")
        status = request.POST.get("status")

        if MayorsPermit.objects.filter(control_no=control_no).exists():
            return JsonResponse({"success": False, "error": f"Control No '{control_no}' is already used."})

        if MayorsPermit.objects.filter(or_no=or_no).exists():
            return JsonResponse({"success": False, "error": f"OR No '{or_no}' is already used."})

        MayorsPermit.objects.create(
            control_no=control_no,
            name=name,
            address=address,
            motorized_operation=motorized_operation,
            business_name=business_name,
            expiry_date=expiry_date,
            amount_paid=amount_paid,
            or_no=or_no,
            issue_date=issue_date,
            issued_at=issued_at,
            mayor=mayor,
            quarter=quarter,
            status=status
        )
        messages.success(request, "Mayor's Permit created successfully!")
        return JsonResponse({"success": True, "message": "Mayor's Permit created successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request method."})


def id_cards(request):
    cards = IDCard.objects.all()
    return render(request, 'myapp/id-cards.html', {'cards': cards})


# ============ ID CARD IMPORT/EXPORT WITH IMAGES ============

def export_idcards_with_images(request):
    """Export all ID Cards with their images as a ZIP file"""
    try:
        # Create a BytesIO object to store the zip file
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create CSV with ID card data
            csv_buffer = StringIO()
            writer = csv.writer(csv_buffer)
            
            # Write header
            writer.writerow([
                'id', 'name', 'id_number', 'address', 'date_of_birth', 'gender',
                'or_number', 'height', 'weight', 'date_issued', 'expiration_date', 'image_filename'
            ])
            
            # Get all ID cards
            cards = IDCard.objects.all()
            
            for card in cards:
                image_filename = ''
                
                # Add image to zip if it exists
                if card.image:
                    # Get image path and filename
                    image_path = card.image.path
                    image_name = os.path.basename(image_path)
                    image_filename = f"images/{image_name}"
                    
                    # Add image to zip
                    try:
                        zip_file.write(image_path, image_filename)
                    except Exception as e:
                        print(f"Error adding image {image_name}: {e}")
                
                # Write card data to CSV
                writer.writerow([
                    card.id,
                    card.name,
                    card.id_number,
                    card.address,
                    card.date_of_birth.strftime("%Y-%m-%d") if card.date_of_birth else '',
                    card.gender,
                    card.or_number or '',
                    card.height or '',
                    card.weight or '',
                    card.date_issued.strftime("%Y-%m-%d") if card.date_issued else '',
                    card.expiration_date.strftime("%Y-%m-%d") if card.expiration_date else '',
                    image_filename
                ])
            
            # Add CSV to zip
            zip_file.writestr('id_cards.csv', csv_buffer.getvalue())
        
        # Prepare response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="id_cards_export.zip"'
        
        return response
        
    except Exception as e:
        messages.error(request, f"Error exporting ID Cards: {str(e)}")
        return redirect('id-cards')


@require_POST
def import_idcards_with_images(request):
    """Import ID Cards from ZIP file containing CSV and images"""
    try:
        uploaded_file = request.FILES.get('zip_file')
        
        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return redirect('id-cards')
        
        if not uploaded_file.name.lower().endswith('.zip'):
            messages.error(request, "Please upload a ZIP file.")
            return redirect('id-cards')
        
        success_count = 0
        errors = []
        
        # Create a temporary directory to extract files
        temp_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Read the CSV file
            csv_path = os.path.join(temp_dir, 'id_cards.csv')
            
            if not os.path.exists(csv_path):
                messages.error(request, "CSV file not found in ZIP.")
                return redirect('id-cards')
            
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Parse dates
                        date_of_birth = None
                        if row.get('date_of_birth'):
                            date_of_birth = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                        
                        date_issued = None
                        if row.get('date_issued'):
                            date_issued = datetime.strptime(row['date_issued'], '%Y-%m-%d').date()
                        
                        expiration_date = None
                        if row.get('expiration_date'):
                            expiration_date = datetime.strptime(row['expiration_date'], '%Y-%m-%d').date()
                        
                        # Handle image - READ INTO MEMORY BEFORE TEMP CLEANUP
                        image_name = None
                        image_data = None
                        if row.get('image_filename'):
                            image_path = os.path.join(temp_dir, row['image_filename'])
                            if os.path.exists(image_path):
                                with open(image_path, 'rb') as img:
                                    image_data = img.read()
                                    image_name = os.path.basename(image_path)
                        
                        # Get or create card
                        card, created = IDCard.objects.update_or_create(
                            id_number=row['id_number'],
                            defaults={
                                'name': row['name'],
                                'address': row['address'],
                                'date_of_birth': date_of_birth,
                                'gender': row['gender'],
                                'or_number': row.get('or_number', ''),
                                'height': float(row['height']) if row.get('height') else None,
                                'weight': float(row['weight']) if row.get('weight') else None,
                                'date_issued': date_issued,
                                'expiration_date': expiration_date,
                            }
                        )
                        
                        # Save image if it exists (AFTER temp data is in memory)
                        if image_data and image_name:
                            if card.image:
                                card.image.delete(save=False)
                            card.image.save(image_name, BytesIO(image_data), save=True)
                        
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
        
        finally:
            # Clean up temp directory AFTER all image data has been read into memory
            shutil.rmtree(temp_dir)
        
        if success_count:
            messages.success(request, f"{success_count} ID Cards imported successfully!")
        
        if errors:
            error_msg = "Some rows could not be imported:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more errors."
            messages.warning(request, error_msg)
        
        return redirect('id-cards')
        
    except Exception as e:
        messages.error(request, f"Error importing ID Cards: {str(e)}")
        return redirect('id-cards')

def update_idcard(request):
    """Handle ID Card update"""
    if request.method == 'POST':
        try:
            # Get the card ID from the form
            card_id = request.POST.get('card_id')
            
            # Get the existing card object
            card = get_object_or_404(IDCard, id=card_id)
            
            # Update fields
            card.name = request.POST.get('name')
            card.id_number = request.POST.get('id_number')
            card.address = request.POST.get('address')
            card.gender = request.POST.get('gender')
            card.or_number = request.POST.get('or_number', '')
            
            # Handle optional fields
            if request.POST.get('date_of_birth'):
                card.date_of_birth = request.POST.get('date_of_birth')
            
            if request.POST.get('height'):
                card.height = request.POST.get('height')
            
            if request.POST.get('weight'):
                card.weight = request.POST.get('weight')
            
            if request.POST.get('date_issued'):
                card.date_issued = request.POST.get('date_issued')
            
            if request.POST.get('expiration_date'):
                card.expiration_date = request.POST.get('expiration_date')
            
            # Handle image upload (only if new image is provided)
            if request.FILES.get('image'):
                # Delete old image if exists
                if card.image:
                    card.image.delete(save=False)
                card.image = request.FILES['image']
            
            # Save the updated card
            card.save()
            
            messages.success(request, 'ID Card updated successfully!')
            return JsonResponse({'status': 'success', 'message': 'ID Card updated successfully!'})
            
        except Exception as e:
            messages.error(request, f'Error updating ID Card: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def add_idcard(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        id_number = request.POST.get("id_number")
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        or_number = request.POST.get("or_number")
        height = request.POST.get("height")
        weight = request.POST.get("weight")
        date_issued = request.POST.get("date_issued")
        expiration_date = request.POST.get("expiration_date")
        image = request.FILES.get("image")  # Optional image

        IDCard.objects.create(
            name=name,
            address=address,
            id_number=id_number,
            date_of_birth=date_of_birth,
            gender=gender,
            or_number=or_number,
            height=height if height else None,
            weight=weight if weight else None,
            date_issued=date_issued,
            expiration_date=expiration_date,
            image=image if image else None,  # Only set if image exists
        )

        messages.success(request, "ID Card added successfully!")
        return JsonResponse({"success": True})

    return JsonResponse({"success": False})

def update_mayors_permit(request, permit_id):

    permit = get_object_or_404(MayorsPermit, id=permit_id)
    old_status = permit.status
    # Extract POST data
    control_no = request.POST.get("control_no")
    name = request.POST.get("name")
    address = request.POST.get("address")
    business_name = request.POST.get("business_name")
    motorized_operation = request.POST.get("motorized_operation")
    or_no = request.POST.get("or_no")
    amount_paid = request.POST.get("amount_paid")
    issue_date = parse_date(request.POST.get("issue_date"))
    expiry_date = parse_date(request.POST.get("expiry_date"))
    issued_at = request.POST.get("issued_at")
    mayor = request.POST.get("mayor")
    quarter = request.POST.get("quarter")
    status = request.POST.get("status")

    # Update fields
    permit.control_no = control_no
    permit.name = name
    permit.address = address
    permit.business_name = business_name
    permit.motorized_operation = motorized_operation
    permit.or_no = or_no
    permit.amount_paid = amount_paid
    permit.issue_date = issue_date
    permit.expiry_date = expiry_date
    permit.issued_at = issued_at
    permit.mayor = mayor
    permit.quarter = quarter
    permit.status = status

    permit.save()
  # ✅ RECORD STATUS CHANGES WITH USER INFO
    if old_status != permit.status:
        # Get user info from session
        user_type = request.session.get('user_type')
        user_id = request.session.get('superadmin_id') if user_type == 'superadmin' else request.session.get('admin_id')
        user_name = request.session.get('full_name')
        
        MayorsPermitHistory.objects.create(
            permit=permit,
            previous_status=old_status,
            new_status=permit.status,
            remarks=f"Status changed from {old_status} to {permit.status}",
            updated_by_type=user_type,
            updated_by_id=user_id,
            updated_by_name=user_name
        )
    messages.success(request, f"Permit for **{permit.name}** updated successfully!")

    # Return JSON for AJAX success
    return JsonResponse({"success": True, "message": "Permit updated successfully!"})

def permit_renewal(request):
    permits = MayorsPermit.objects.all()
    return render(request, 'myapp/permit-renewal.html', {'permits': permits})

def permit_detail_api(request, control_no):
    permit = get_object_or_404(MayorsPermit, control_no=control_no)

    data = {
        "control_no": permit.control_no,
        "name": permit.name,
        "address": permit.address,
        "business_name": permit.business_name,
        "status": permit.status,
        "issue_date": permit.issue_date.strftime("%Y-%m-%d"),
        "expiry_date": permit.expiry_date.strftime("%Y-%m-%d"),
        "mayor": permit.mayor,
        "quarter": permit.get_quarter_display(),
    }

    return JsonResponse(data, json_dumps_params={'indent': 4})

def print_mayors_permit(request, pk):
    permit = get_object_or_404(MayorsPermit, pk=pk)
    return render(request, "myapp/mayors-permit-print.html", {"permit": permit})


def mtop(request):
    mtops = Mtop.objects.all()
    return render(request, 'myapp/mtop.html', {'mtops': mtops})


def import_mtop(request):
    """Import MTOP records from CSV or Excel file"""
    if request.method != "POST":
        messages.error(request, 'Invalid request method')
        return redirect('mtop')
    
    # Check if file exists in request
    uploaded_file = request.FILES.get('import_file')
    if not uploaded_file:
        messages.error(request, "No file uploaded.")
        return redirect('mtop')
    
    file_name = uploaded_file.name.lower()
    is_excel = file_name.endswith(('.xlsx', '.xls'))
    is_csv = file_name.endswith('.csv')
    
    if not (is_csv or is_excel):
        messages.error(request, "Please upload a CSV or Excel file (.csv, .xlsx, .xls)")
        return redirect('mtop')
    
    errors = []
    success_count = 0
    
    # Expected header columns
    expected_header = ['name', 'case_no', 'address', 'no_of_units', 'route_operation',
                      'make', 'motor_no', 'chasses_no', 'plate_no', 'date',
                      'municipal_treasurer', 'officer_in_charge', 'mayor']
    
    def normalize_header(header):
        """Convert header to lowercase, replace spaces/periods with underscores, and fix common variations"""
        normalized = []
        for h in header:
            # Convert to lowercase, strip whitespace
            h = h.strip().lower()
            # Replace spaces and periods with underscores
            h = h.replace(' ', '_').replace('.', '')
            # Fix common spelling variations
            h = h.replace('chassis', 'chasses')  # chassis -> chasses
            normalized.append(h)
        return normalized
    
    try:
        if is_excel:
            # Handle Excel file
            wb = openpyxl.load_workbook(uploaded_file)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            
            if not rows:
                messages.error(request, "Excel file is empty.")
                return redirect('mtop')
            
            # Validate and normalize header
            raw_header = [str(cell).strip() if cell else '' for cell in rows[0]]
            normalized_header = normalize_header(raw_header)
            
            if normalized_header != expected_header:
                messages.error(request, f"Invalid Excel header. Expected: {', '.join(expected_header)}. Got: {', '.join(normalized_header)}")
                return redirect('mtop')
            
            # Skip header row
            data_rows = rows[1:]
            
            for i, row in enumerate(data_rows, start=2):
                if not row or all(cell is None for cell in row):
                    continue
                
                if len(row) < len(expected_header):
                    errors.append(f"Row {i}: Incorrect number of columns ({len(row)}). Expected {len(expected_header)}.")
                    continue
                
                try:
                    # Handle date parsing for Excel - keep original date type
                    def parse_excel_date(date_val):
                        if isinstance(date_val, datetime):
                            return date_val.date()
                        elif isinstance(date_val, str):
                            return datetime.strptime(date_val.strip(), "%Y-%m-%d").date()
                        else:
                            return date_val
                    
                    date_obj = parse_excel_date(row[9])
                    
                    try:
                        no_of_units = int(float(row[3])) if row[3] else 1
                    except ValueError:
                        raise ValueError(f"Invalid no_of_units '{row[3]}'")
                    
                    Mtop.objects.update_or_create(
                        case_no=str(row[1]).strip() if row[1] else '',
                        defaults={
                            "name": str(row[0]).strip() if row[0] else '',
                            "address": str(row[2]).strip() if row[2] else '',
                            "no_of_units": no_of_units,
                            "route_operation": str(row[4]).strip() if row[4] else '',
                            "make": str(row[5]).strip() if row[5] else '',
                            "motor_no": str(row[6]).strip() if row[6] else '',
                            "chasses_no": str(row[7]).strip() if row[7] else '',
                            "plate_no": str(row[8]).strip() if row[8] else '',
                            "date": date_obj,
                            "municipal_treasurer": str(row[10]).strip() if row[10] else '',
                            "officer_in_charge": str(row[11]).strip() if row[11] else '',
                            "mayor": str(row[12]).strip() if row[12] else '',
                        },
                    )
                    success_count += 1
                
                except ValueError as ve:
                    errors.append(f"Row {i}: Value error - {ve}")
                except Exception as e:
                    errors.append(f"Row {i}: {e}")
        
        else:
            # Handle CSV file
            file_data = uploaded_file.read().decode("utf-8-sig").splitlines()
            reader = csv.reader(file_data)
            raw_header = next(reader)
            
            # Validate and normalize header columns
            normalized_header = normalize_header(raw_header)
            
            if normalized_header != expected_header:
                messages.error(request, f"Invalid CSV header. Expected: {', '.join(expected_header)}. Got: {', '.join(normalized_header)}")
                return redirect('mtop')
            
            for i, row in enumerate(reader, start=2):
                # Strip whitespace from all columns
                row = [c.strip() for c in row]
                
                if len(row) != len(expected_header):
                    errors.append(f"Row {i}: Incorrect number of columns ({len(row)}). Expected {len(expected_header)}.")
                    continue
                
                try:
                    date_obj = datetime.strptime(row[9], "%Y-%m-%d").date()
                    
                    try:
                        no_of_units = int(row[3])
                    except ValueError:
                        raise ValueError(f"Invalid no_of_units '{row[3]}'")
                    
                    Mtop.objects.update_or_create(
                        case_no=row[1],
                        defaults={
                            "name": row[0],
                            "address": row[2],
                            "no_of_units": no_of_units,
                            "route_operation": row[4],
                            "make": row[5],
                            "motor_no": row[6],
                            "chasses_no": row[7],
                            "plate_no": row[8],
                            "date": date_obj,
                            "municipal_treasurer": row[10],
                            "officer_in_charge": row[11],
                            "mayor": row[12],
                        },
                    )
                    success_count += 1
                
                except ValueError as ve:
                    errors.append(f"Row {i}: Value error - {ve}")
                except Exception as e:
                    errors.append(f"Row {i}: {e}")
        
        if success_count:
            messages.success(request, f"{success_count} MTOP records imported successfully!")
        
        if errors:
            messages.warning(request, "Some rows could not be imported:\n" + "\n".join(errors[:10]))
            if len(errors) > 10:
                messages.warning(request, f"... and {len(errors) - 10} more errors.")
    
    except Exception as e:
        messages.error(request, f"Failed to read file: {e}")
    
    return redirect('mtop')


def export_mtop(request):
    """Export MTOP records to CSV or Excel file based on format parameter"""
    export_format = request.GET.get('format', 'csv').lower()
    
    if export_format == 'excel':
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "MTOP Records"
        
        # Define styles
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        
        # Write headers
        headers = [
            'name', 'case_no', 'address', 'no_of_units', 'route_operation',
            'make', 'motor_no', 'chasses_no', 'plate_no', 'date',
            'municipal_treasurer', 'officer_in_charge', 'mayor'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
        
        # Write data
        mtops = Mtop.objects.all().order_by('id')
        for row_num, mtop in enumerate(mtops, 2):
            data = [
                mtop.name,
                mtop.case_no,
                mtop.address,
                mtop.no_of_units,
                mtop.route_operation,
                mtop.make,
                mtop.motor_no,
                mtop.chasses_no,
                mtop.plate_no,
                mtop.date,
                mtop.municipal_treasurer,
                mtop.officer_in_charge,
                mtop.mayor,
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="mtop_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        wb.save(response)
        return response
    
    else:  # Default to CSV
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="mtop_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'name', 'case_no', 'address', 'no_of_units', 'route_operation',
            'make', 'motor_no', 'chasses_no', 'plate_no', 'date',
            'municipal_treasurer', 'officer_in_charge', 'mayor'
        ])
        
        # Write data
        mtops = Mtop.objects.all().order_by('id')
        for mtop in mtops:
            writer.writerow([
                mtop.name,
                mtop.case_no,
                mtop.address,
                mtop.no_of_units,
                mtop.route_operation,
                mtop.make,
                mtop.motor_no,
                mtop.chasses_no,
                mtop.plate_no,
                mtop.date.strftime('%Y-%m-%d'),
                mtop.municipal_treasurer,
                mtop.officer_in_charge,
                mtop.mayor,
            ])
        
        return response

def import_franchise(request):
    """Import Franchise records from CSV or Excel file"""
    if request.method != "POST":
        messages.error(request, 'Invalid request method')
        return redirect('franchise')
    
    # Check if file exists in request
    uploaded_file = request.FILES.get('import_file')
    if not uploaded_file:
        messages.error(request, "No file uploaded.")
        return redirect('franchise')
    
    file_name = uploaded_file.name.lower()
    is_excel = file_name.endswith(('.xlsx', '.xls'))
    is_csv = file_name.endswith('.csv')
    
    if not (is_csv or is_excel):
        messages.error(request, "Please upload a CSV or Excel file (.csv, .xlsx, .xls)")
        return redirect('franchise')
    
    errors = []
    success_count = 0
    
    # Expected header columns
    expected_header = ['name', 'denomination', 'plate_no', 'valid_until', 'motor_no',
                      'authorized_no', 'chassis_no', 'authorized_route', 'purpose',
                      'official_receipt_no', 'date', 'amount_paid', 'municipal_treasurer']
    
    def normalize_header(header):
        """Convert header to lowercase, replace spaces/periods with underscores, and fix common variations"""
        normalized = []
        for h in header:
            h = h.lower().strip()
            h = h.replace(' ', '_').replace('.', '')
            h = h.replace('chassis', 'chassis').replace('authorized', 'authorized')
            normalized.append(h)
        return normalized
    
    try:
        if is_excel:
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        # Normalize DataFrame columns
        df.columns = normalize_header(df.columns)
        
        for idx, row in df.iterrows():
            try:
                # Check for duplicates
                if Franchise.objects.filter(plate_no=row['plate_no']).exists():
                    errors.append(f"Row {idx+2}: Plate No '{row['plate_no']}' already exists.")
                    continue
                
                if Franchise.objects.filter(authorized_no=row['authorized_no']).exists():
                    errors.append(f"Row {idx+2}: Authorized No '{row['authorized_no']}' already exists.")
                    continue
                
                # Convert amount_paid to int (handle decimal strings)
                try:
                    amount_paid = int(float(row.get('amount_paid', 0)))
                except (ValueError, TypeError):
                    amount_paid = 0
                
                # Create franchise record
                Franchise.objects.create(
                    name=row.get('name', ''),
                    denomination=row.get('denomination', ''),
                    plate_no=row.get('plate_no', ''),
                    valid_until=row.get('valid_until', ''),
                    motor_no=row.get('motor_no', ''),
                    authorized_no=row.get('authorized_no', ''),
                    chassis_no=row.get('chassis_no', ''),
                    authorized_route=row.get('authorized_route', ''),
                    purpose=row.get('purpose', ''),
                    official_receipt_no=row.get('official_receipt_no', ''),
                    date=row.get('date', ''),
                    amount_paid=amount_paid,
                    municipal_treasurer=row.get('municipal_treasurer', '')
                )
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f"Successfully imported {success_count} franchise record(s).")
        
        if errors:
            for error in errors:
                messages.warning(request, error)
        
        return redirect('franchise')
        
    except Exception as e:
        messages.error(request, f"Error processing file: {str(e)}")
        return redirect('franchise')


def export_franchise(request):
    """Export Franchise records to CSV or Excel file based on format parameter"""
    export_format = request.GET.get('format', 'csv').lower()
    
    if export_format == 'excel':
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Franchise Records"
        
        # Define styles
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        
        # Write headers
        headers = [
            'name', 'denomination', 'plate_no', 'valid_until', 'motor_no',
            'authorized_no', 'chassis_no', 'authorized_route', 'purpose',
            'official_receipt_no', 'date', 'amount_paid', 'municipal_treasurer'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
        
        # Write data
        franchises = Franchise.objects.all().order_by('id')
        for row_num, franchise in enumerate(franchises, 2):
            data = [
                franchise.name,
                franchise.denomination,
                franchise.plate_no,
                franchise.valid_until,
                franchise.motor_no,
                franchise.authorized_no,
                franchise.chassis_no,
                franchise.authorized_route,
                franchise.purpose,
                franchise.official_receipt_no,
                franchise.date,
                franchise.amount_paid,
                franchise.municipal_treasurer,
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
        
        # Auto adjust column width
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2
        
        # Save to BytesIO
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="franchise_records.xlsx"'
        wb.save(response)
        return response
    
    else:
        # CSV export
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="franchise_records.csv"'
        
        writer = csv.writer(response)
        headers = [
            'name', 'denomination', 'plate_no', 'valid_until', 'motor_no',
            'authorized_no', 'chassis_no', 'authorized_route', 'purpose',
            'official_receipt_no', 'date', 'amount_paid', 'municipal_treasurer'
        ]
        writer.writerow(headers)
        
        franchises = Franchise.objects.all().order_by('id')
        for franchise in franchises:
            writer.writerow([
                franchise.name,
                franchise.denomination,
                franchise.plate_no,
                franchise.valid_until,
                franchise.motor_no,
                franchise.authorized_no,
                franchise.chassis_no,
                franchise.authorized_route,
                franchise.purpose,
                franchise.official_receipt_no,
                franchise.date,
                franchise.amount_paid,
                franchise.municipal_treasurer,
            ])
        
        return response

def mtop_print(request, pk):
    mtop = Mtop.objects.get(pk=pk)
    return render(request, 'myapp/mtop-print.html', {'mtop': mtop})

def franchise(request):
    franchises = Franchise.objects.all().order_by('-date')  # latest first
    return render(request, 'myapp/franchise.html', {'franchises': franchises}) 


def mayors_permit_tricycle(request):
    permits = MayorsPermitTricycle.objects.all()
    return render(request, 'myapp/mayors-permit-tri.html', {'permits': permits})


def mayors_permit_tri_history_data(request, permit_id):
    """API endpoint to fetch status history for a specific tricycle permit"""
    try:
        # Get the permit
        permit = get_object_or_404(MayorsPermitTricycle, id=permit_id)
        
        # Get all history records for this permit
        history_records = MayorsPermitTricycleHistory.objects.filter(
            permit_id=permit_id
        ).order_by('-activated_at')
        
        # Format history data
        history_data = []
        for record in history_records:
            # Determine who changed it
            if record.updated_by_name:
                changed_by = record.updated_by_name
            elif record.updated_by_type:
                changed_by = record.updated_by_type.capitalize()
            else:
                changed_by = 'System'
            
            history_data.append({
                'date': record.activated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'old_status': record.previous_status.capitalize(),
                'new_status': record.new_status.capitalize(),
                'changed_by': changed_by,
                'reason': record.remarks or ''
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'permit_info': {
                    'control_no': permit.control_no,
                    'name': permit.name,
                    'current_status': permit.status
                },
                'history': history_data
            }
        })
        
    except MayorsPermitTricycle.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Permit not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def mayors_permit_tricycle_datatable(request):
    """Server-side processing endpoint for DataTables"""
    
    # DataTables parameters
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Base queryset
    queryset = MayorsPermitTricycle.objects.all()
    
    # Global search
    if search_value:
        queryset = queryset.filter(
            Q(control_no__icontains=search_value) |
            Q(name__icontains=search_value) |
            Q(address__icontains=search_value) |
            Q(business_name__icontains=search_value) |
            Q(or_no__icontains=search_value)
        )
    
    # Column-specific search
    for i in range(14):
        column_search = request.GET.get(f'columns[{i}][search][value]', '')
        if column_search:
            if i == 0:  # Control No
                queryset = queryset.filter(control_no__icontains=column_search)
            elif i == 1:  # Status - exact match
                queryset = queryset.filter(status__iexact=column_search)
            elif i == 2:  # Name
                queryset = queryset.filter(name__icontains=column_search)
            elif i == 3:  # Address
                queryset = queryset.filter(address__icontains=column_search)
            elif i == 4:  # Motorized Operation
                queryset = queryset.filter(motorized_operation__icontains=column_search)
            elif i == 5:  # Business Name
                queryset = queryset.filter(business_name__icontains=column_search)
            elif i == 6:  # Expiry Date
                queryset = queryset.filter(expiry_date__icontains=column_search)
            elif i == 7:  # Amount Paid
                queryset = queryset.filter(amount_paid__icontains=column_search)
            elif i == 8:  # OR No
                queryset = queryset.filter(or_no__icontains=column_search)
            elif i == 9:  # Issue Date
                queryset = queryset.filter(issue_date__icontains=column_search)
            elif i == 10:  # Issued At
                queryset = queryset.filter(issued_at__icontains=column_search)
            elif i == 11:  # Mayor
                queryset = queryset.filter(mayor__icontains=column_search)
            elif i == 12:  # Quarter
                queryset = queryset.filter(quarter__icontains=column_search)
    
    # Total records
    total_records = MayorsPermitTricycle.objects.count()
    filtered_records = queryset.count()
    
    # Pagination
    permits = queryset[start:start + length]
    
    # Format data
    data = []
    for permit in permits:
        # Status badge HTML
        if permit.status == "active":
            status_html = '<span class="badge badge-success">Active</span>'
        elif permit.status == "inactive":
            status_html = '<span class="badge badge-warning">Inactive</span>'
        elif permit.status == "expired":
            status_html = '<span class="badge badge-danger">Expired</span>'
        else:
            status_html = f'<span class="badge badge-secondary">{permit.status.capitalize()}</span>'
        
        # Action buttons HTML
        action_html = f'''
        <div class="btn-group" role="group">
             <button class="btn btn-sm btn-info btn-view" title="View Details" 
                data-id="{permit.id}"
                data-control_no="{permit.control_no}"
                data-status="{permit.status}"
                data-name="{permit.name}"
                data-address="{permit.address}"
                data-motorized_operation="{permit.motorized_operation}"
                data-business_name="{permit.business_name}"
                data-expiry_date="{permit.expiry_date}"
                data-amount_paid="{permit.amount_paid}"
                data-or_no="{permit.or_no}"
                data-issue_date="{permit.issue_date}"
                data-issued_at="{permit.issued_at}"
                data-mayor="{permit.mayor}"
                data-quarter="{permit.quarter}">
                <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-sm btn-primary btn-print" title="Print" 
                data-permit-id="{permit.id}"
                data-control-no="{permit.control_no}"
                data-name="{permit.name}"
                data-address="{permit.address}"
                data-motorized="{permit.motorized_operation}"
                data-business="{permit.business_name}"
                data-expiry="{permit.expiry_date}"
                data-quarter="{permit.quarter}"
                data-amount="{permit.amount_paid}"
                data-or="{permit.or_no}"
                data-issue="{permit.issue_date}"
                data-issued-at="{permit.issued_at}"
                data-mayor="{permit.mayor}">
                <i class="fas fa-print"></i>
            </button>
            <button type="button" class="btn btn-sm btn-warning btn-update" title="Update"
                data-id="{permit.id}"
                data-control_no="{permit.control_no}"
                data-status="{permit.status}"
                data-name="{permit.name}"
                data-address="{permit.address}"
                data-motorized_operation="{permit.motorized_operation}"
                data-business_name="{permit.business_name}"
                data-expiry_date="{permit.expiry_date}"
                data-amount_paid="{permit.amount_paid}"
                data-or_no="{permit.or_no}"
                data-issue_date="{permit.issue_date}"
                data-issued_at="{permit.issued_at}"
                data-mayor="{permit.mayor}"
                data-quarter="{permit.quarter}">
                <i class="fas fa-edit"></i>
            </button>
            <button type="button" class="btn btn-sm btn-secondary btn-history" data-id="{permit.id}" title="History">
                <i class="fas fa-history"></i>
            </button>
        </div>
        '''
        
        data.append([
            permit.control_no,
            status_html,
            permit.name,
            permit.address,
            permit.motorized_operation or '',
            permit.business_name or '',
            permit.expiry_date.strftime('%Y-%m-%d'),
            str(permit.amount_paid),
            permit.or_no,
            permit.issue_date.strftime('%Y-%m-%d'),
            permit.issued_at or '',
            permit.mayor or '',
            permit.get_quarter_display(),
            action_html,
            permit.id,  # Hidden column for ID
            permit.status  # Hidden column for raw status value
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })

def add_permit_tri(request):
    if request.method == 'POST':
        try:
            # Get all form data
            control_no = request.POST.get('control_no')
            name = request.POST.get('name')
            address = request.POST.get('address')
            motorized_operation = request.POST.get('motorized_operation')
            business_name = request.POST.get('business_name')
            expiry_date = request.POST.get('expiry_date')
            amount_paid = request.POST.get('amount_paid')
            or_no = request.POST.get('or_no')
            issue_date = request.POST.get('issue_date')
            issued_at = request.POST.get('issued_at')
            mayor = request.POST.get('mayor')
            quarter = request.POST.get('quarter')
            status = request.POST.get('status')

            # Create new permit
            permit = MayorsPermitTricycle.objects.create(
                control_no=control_no,
                name=name,
                address=address,
                motorized_operation=motorized_operation,
                business_name=business_name,
                expiry_date=expiry_date,
                amount_paid=int(amount_paid),
                or_no=or_no,
                issue_date=issue_date,
                issued_at=issued_at,
                mayor=mayor,
                quarter=quarter,
                status=status
            )

            messages.success(request, f'Permit {control_no} has been successfully added!')
            return redirect('mayors-permit-tricycle')  # Replace with your actual list view URL name
        
        except Exception as e:
            messages.error(request, f'Error adding permit: {str(e)}')
            return redirect('mayors-permit-tricycle')  # Replace with your actual list view URL name
    
    messages.error(request, 'Invalid request method')
    return redirect('mayors-permit-tricycle')  # Replace with your actual list view URL name

def export_mayors_permit(request):
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'excel':
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Mayors Permit"
        
        # Header styling
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        # Excel Header
        headers = [
            'Control No', 'Name', 'Address', 'Motorized Operation',
            'Business Name', 'Expiry Date', 'Amount Paid', 'OR No',
            'Issue Date', 'Issued At', 'Mayor', 'Quarter', 'Status'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
        
        # Excel Rows
        for row_num, p in enumerate(MayorsPermit.objects.all(), 2):
            ws.cell(row=row_num, column=1, value=p.control_no)
            ws.cell(row=row_num, column=2, value=p.name)
            ws.cell(row=row_num, column=3, value=p.address)
            ws.cell(row=row_num, column=4, value=p.motorized_operation)
            ws.cell(row=row_num, column=5, value=p.business_name)
            ws.cell(row=row_num, column=6, value=str(p.expiry_date) if p.expiry_date else '')
            ws.cell(row=row_num, column=7, value=p.amount_paid)
            ws.cell(row=row_num, column=8, value=p.or_no)
            ws.cell(row=row_num, column=9, value=str(p.issue_date) if p.issue_date else '')
            ws.cell(row=row_num, column=10, value=p.issued_at)
            ws.cell(row=row_num, column=11, value=p.mayor)
            ws.cell(row=row_num, column=12, value=p.quarter)
            ws.cell(row=row_num, column=13, value=p.status)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="mayors_permit.xlsx"'
        wb.save(response)
        return response
    
    else:  # CSV format (default)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mayors_permit.csv"'
        
        writer = csv.writer(response)
        
        # CSV Header
        writer.writerow([
            'control_no', 'name', 'address', 'motorized_operation',
            'business_name', 'expiry_date', 'amount_paid', 'or_no',
            'issue_date', 'issued_at', 'mayor', 'quarter', 'status'
        ])
        
        # CSV Rows
        for p in MayorsPermit.objects.all():
            writer.writerow([
                p.control_no, p.name, p.address, p.motorized_operation,
                p.business_name, p.expiry_date, p.amount_paid, p.or_no,
                p.issue_date, p.issued_at, p.mayor, p.quarter, p.status
            ])
        
        return response

def export_mayors_permit_tri(request):
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'excel':
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Mayors Permit Tricycle"
        
        # Header styling
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        # Excel Header
        headers = [
            'Control No', 'Name', 'Address', 'Motorized Operation',
            'Business Name', 'Expiry Date', 'Amount Paid', 'OR No',
            'Issue Date', 'Issued At', 'Mayor', 'Quarter', 'Status'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
        
        # Excel Rows
        for row_num, p in enumerate(MayorsPermitTricycle.objects.all(), 2):
            ws.cell(row=row_num, column=1, value=p.control_no)
            ws.cell(row=row_num, column=2, value=p.name)
            ws.cell(row=row_num, column=3, value=p.address)
            ws.cell(row=row_num, column=4, value=p.motorized_operation)
            ws.cell(row=row_num, column=5, value=p.business_name)
            ws.cell(row=row_num, column=6, value=str(p.expiry_date) if p.expiry_date else '')
            ws.cell(row=row_num, column=7, value=p.amount_paid)
            ws.cell(row=row_num, column=8, value=p.or_no)
            ws.cell(row=row_num, column=9, value=str(p.issue_date) if p.issue_date else '')
            ws.cell(row=row_num, column=10, value=p.issued_at)
            ws.cell(row=row_num, column=11, value=p.mayor)
            ws.cell(row=row_num, column=12, value=p.quarter)
            ws.cell(row=row_num, column=13, value=p.status)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="mayors_permit_tricycle.xlsx"'
        wb.save(response)
        return response
    
    else:  # CSV format (default)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mayors_permit_tricycle.csv"'
        
        writer = csv.writer(response)
        
        # CSV Header
        writer.writerow([
            'control_no', 'name', 'address', 'motorized_operation',
            'business_name', 'expiry_date', 'amount_paid', 'or_no',
            'issue_date', 'issued_at', 'mayor', 'quarter', 'status'
        ])
        
        # CSV Rows
        for p in MayorsPermitTricycle.objects.all():
            writer.writerow([
                p.control_no, p.name, p.address, p.motorized_operation,
                p.business_name, p.expiry_date, p.amount_paid, p.or_no,
                p.issue_date, p.issued_at, p.mayor, p.quarter, p.status
            ])
        
        return response
    
def import_mayors_permit_tri(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("csv_file")

        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return redirect("mayors-permit-tricycle")

        file_name = uploaded_file.name.lower()
        is_excel = file_name.endswith(('.xlsx', '.xls'))
        is_csv = file_name.endswith('.csv')

        if not (is_csv or is_excel):
            messages.error(request, "Please upload a CSV or Excel file (.csv, .xlsx, .xls)")
            return redirect("mayors-permit-tricycle")

        errors = []
        success_count = 0

        # Expected header columns (with underscores)
        expected_header = ['control_no', 'name', 'address', 'motorized_operation', 
                          'business_name', 'expiry_date', 'amount_paid', 'or_no', 
                          'issue_date', 'issued_at', 'mayor', 'quarter', 'status']

        def normalize_header(header):
            """Convert header to lowercase and replace spaces with underscores"""
            return [h.strip().lower().replace(' ', '_') for h in header]

        try:
            if is_excel:
                # Handle Excel file
                wb = load_workbook(uploaded_file)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                
                if not rows:
                    messages.error(request, "Excel file is empty.")
                    return redirect("mayors-permit-tricycle")
                
                # Validate and normalize header
                raw_header = [str(cell).strip() if cell else '' for cell in rows[0]]
                normalized_header = normalize_header(raw_header)
                
                if normalized_header != expected_header:
                    messages.error(request, f"Invalid Excel header. Expected: {', '.join(expected_header)}. Got: {', '.join(normalized_header)}")
                    return redirect('mayors-permit-tricycle')
                
                # Skip header row
                data_rows = rows[1:]
                
                for i, row in enumerate(data_rows, start=2):
                    if not row or all(cell is None for cell in row):
                        continue
                        
                    # Strip whitespace from all columns
                    row = [str(cell).strip() if cell is not None else '' for cell in row]
                    
                    if len(row) < len(expected_header):
                        errors.append(f"Row {i}: Incorrect number of columns ({len(row)}). Expected {len(expected_header)}.")
                        continue

                    try:
                        # Handle date parsing for Excel
                        def parse_date(date_val):
                            if isinstance(date_val, datetime):
                                return date_val.date()
                            elif isinstance(date_val, str):
                                return datetime.strptime(date_val, "%Y-%m-%d").date()
                            else:
                                return date_val

                        issue_date = parse_date(row[8])
                        expiry_date = parse_date(row[5])
                        
                        try:
                            amount_paid = int(float(row[6])) if row[6] else 0
                        except ValueError:
                            raise ValueError(f"Invalid amount_paid '{row[6]}'")

                        MayorsPermitTricycle.objects.update_or_create(
                            control_no=str(row[0]) if row[0] else '',
                            defaults={
                                "name": str(row[1]) if row[1] else '',
                                "address": str(row[2]) if row[2] else '',
                                "motorized_operation": str(row[3]) if row[3] else '',
                                "business_name": str(row[4]) if row[4] else '',
                                "expiry_date": expiry_date,
                                "amount_paid": amount_paid,
                                "or_no": str(row[7]) if row[7] else '',
                                "issue_date": issue_date,
                                "issued_at": str(row[9]) if row[9] else '',
                                "mayor": str(row[10]) if row[10] else '',
                                "quarter": str(row[11]) if row[11] else '',
                                "status": str(row[12]) if row[12] else 'active',
                            },
                        )
                        success_count += 1

                    except ValueError as ve:
                        errors.append(f"Row {i}: Value error - {ve}")
                    except Exception as e:
                        errors.append(f"Row {i}: {e}")

            else:
                # Handle CSV file
                file_data = uploaded_file.read().decode("utf-8-sig").splitlines()
                reader = csv.reader(file_data)
                raw_header = next(reader)
                
                # Validate and normalize header columns
                normalized_header = normalize_header(raw_header)
                
                if normalized_header != expected_header:
                    messages.error(request, f"Invalid CSV header. Expected: {', '.join(expected_header)}. Got: {', '.join(normalized_header)}")
                    return redirect('mayors-permit-tricycle')

                for i, row in enumerate(reader, start=2):
                    # Strip whitespace from all columns
                    row = [c.strip() for c in row]

                    if len(row) != len(expected_header):
                        errors.append(f"Row {i}: Incorrect number of columns ({len(row)}). Expected {len(expected_header)}.")
                        continue

                    try:
                        issue_date = datetime.strptime(row[8], "%Y-%m-%d").date()
                        expiry_date = datetime.strptime(row[5], "%Y-%m-%d").date()

                        try:
                            amount_paid = int(row[6])
                        except ValueError:
                            raise ValueError(f"Invalid amount_paid '{row[6]}'")

                        MayorsPermitTricycle.objects.update_or_create(
                            control_no=row[0],
                            defaults={
                                "name": row[1],
                                "address": row[2],
                                "motorized_operation": row[3],
                                "business_name": row[4],
                                "expiry_date": expiry_date,
                                "amount_paid": amount_paid,
                                "or_no": row[7],
                                "issue_date": issue_date,
                                "issued_at": row[9],
                                "mayor": row[10],
                                "quarter": row[11],
                                "status": row[12],
                            },
                        )
                        success_count += 1

                    except ValueError as ve:
                        errors.append(f"Row {i}: Value error - {ve}")
                    except Exception as e:
                        errors.append(f"Row {i}: {e}")

            if success_count:
                messages.success(request, f"{success_count} permits imported successfully!")

            if errors:
                messages.warning(request, "Some rows could not be imported:\n" + "\n".join(errors[:10]))
                if len(errors) > 10:
                    messages.warning(request, f"... and {len(errors) - 10} more errors.")

        except Exception as e:
            messages.error(request, f"Failed to read file: {e}")

        return redirect("mayors-permit-tricycle")

    messages.error(request, 'Invalid request method')
    return redirect('mayors-permit-tricycle')

def import_mayors_permit(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("csv_file")

        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return redirect("mayors-permit")

        file_name = uploaded_file.name.lower()
        is_excel = file_name.endswith(('.xlsx', '.xls'))
        is_csv = file_name.endswith('.csv')

        if not (is_csv or is_excel):
            messages.error(request, "Please upload a CSV or Excel file (.csv, .xlsx, .xls)")
            return redirect("mayors-permit")

        errors = []
        success_count = 0

        # Expected header columns
        expected_header = ['control_no', 'name', 'address', 'motorized_operation', 
                          'business_name', 'expiry_date', 'amount_paid', 'or_no', 
                          'issue_date', 'issued_at', 'mayor', 'quarter', 'status']

        def normalize_header(header):
            """Convert header to lowercase and replace spaces with underscores"""
            return [h.strip().lower().replace(' ', '_') for h in header]

        try:
            if is_excel:
                # Handle Excel file
                wb = load_workbook(uploaded_file)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                
                if not rows:
                    messages.error(request, "Excel file is empty.")
                    return redirect("mayors-permit")
                
                # Validate and normalize header
                raw_header = [str(cell).strip() if cell else '' for cell in rows[0]]
                normalized_header = normalize_header(raw_header)
                
                if normalized_header != expected_header:
                    messages.error(request, f"Invalid Excel header. Expected: {', '.join(expected_header)}. Got: {', '.join(normalized_header)}")
                    return redirect('mayors-permit')
                
                # Skip header row
                data_rows = rows[1:]
                
                for i, row in enumerate(data_rows, start=2):
                    if not row or all(cell is None for cell in row):
                        continue
                        
                    if len(row) < 13:
                        errors.append(f"Row {i}: Incorrect number of columns ({len(row)}).")
                        continue

                    try:
                        # Handle date parsing for Excel
                        def parse_date(date_val):
                            if isinstance(date_val, datetime):
                                return date_val.date()
                            elif isinstance(date_val, str):
                                return datetime.strptime(date_val, "%Y-%m-%d").date()
                            else:
                                return date_val

                        issue_date = parse_date(row[8])
                        expiry_date = parse_date(row[5])
                        amount_paid = int(float(row[6])) if row[6] else 0

                        MayorsPermit.objects.update_or_create(
                            control_no=str(row[0]) if row[0] else '',
                            defaults={
                                "name": str(row[1]) if row[1] else '',
                                "address": str(row[2]) if row[2] else '',
                                "motorized_operation": str(row[3]) if row[3] else '',
                                "business_name": str(row[4]) if row[4] else '',
                                "expiry_date": expiry_date,
                                "amount_paid": amount_paid,
                                "or_no": str(row[7]) if row[7] else '',
                                "issue_date": issue_date,
                                "issued_at": str(row[9]) if row[9] else '',
                                "mayor": str(row[10]) if row[10] else '',
                                "quarter": str(row[11]) if row[11] else '',
                                "status": str(row[12]) if row[12] else 'active',
                            },
                        )
                        success_count += 1

                    except ValueError as ve:
                        errors.append(f"Row {i}: Value error - {ve}")
                    except Exception as e:
                        errors.append(f"Row {i}: {e}")

            else:
                # Handle CSV file
                file_data = uploaded_file.read().decode("utf-8").splitlines()
                reader = csv.reader(file_data)
                raw_header = next(reader)
                
                # Validate and normalize header
                normalized_header = normalize_header(raw_header)
                
                if normalized_header != expected_header:
                    messages.error(request, f"Invalid CSV header. Expected: {', '.join(expected_header)}. Got: {', '.join(normalized_header)}")
                    return redirect('mayors-permit')

                for i, row in enumerate(reader, start=2):
                    if len(row) != 13:
                        errors.append(f"Row {i}: Incorrect number of columns ({len(row)}).")
                        continue

                    try:
                        issue_date = datetime.strptime(row[8], "%Y-%m-%d").date()
                        expiry_date = datetime.strptime(row[5], "%Y-%m-%d").date()
                        amount_paid = int(row[6])

                        MayorsPermit.objects.update_or_create(
                            control_no=row[0],
                            defaults={
                                "name": row[1],
                                "address": row[2],
                                "motorized_operation": row[3],
                                "business_name": row[4],
                                "expiry_date": expiry_date,
                                "amount_paid": amount_paid,
                                "or_no": row[7],
                                "issue_date": issue_date,
                                "issued_at": row[9],
                                "mayor": row[10],
                                "quarter": row[11],
                                "status": row[12],
                            },
                        )
                        success_count += 1

                    except ValueError as ve:
                        errors.append(f"Row {i}: Value error - {ve}")
                    except Exception as e:
                        errors.append(f"Row {i}: {e}")

            if success_count:
                messages.success(request, f"{success_count} permits imported successfully!")

            if errors:
                messages.warning(request, "Some rows could not be imported:\n" + "\n".join(errors[:10]))
                if len(errors) > 10:
                    messages.warning(request, f"... and {len(errors) - 10} more errors.")

        except Exception as e:
            messages.error(request, f"Failed to read file: {e}")

        return redirect("mayors-permit")


def sample_print(request):
    return render(request, 'myapp/sample-print.html')


def mayors_permit_history(request, permit_id):
    permit = get_object_or_404(MayorsPermit, id=permit_id)
    history = permit.histories.order_by('-activated_at')

    return render(request, 'myapp/mayors-permit-history.html', {
        'permit': permit,
        'history': history
    })


