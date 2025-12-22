import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from .models import Admin, MayorsPermit, IDCard, Mtop, Franchise, MayorsPermitTricycle, SuperAdmin
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from .forms import CSVUploadForm
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_http_methods
from functools import wraps

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
    try:
        # Get the permit object
        permit = get_object_or_404(MayorsPermitTricycle, id=permit_id)
        
        # Parse JSON data
        data = json.loads(request.body)
        
        # Update fields
        permit.control_no = data.get('control_no')
        permit.name = data.get('name')
        permit.address = data.get('address')
        permit.motorized_operation = data.get('motorized_operation')
        permit.business_name = data.get('business_name')
        
        # Parse and update dates
        if data.get('issue_date'):
            permit.issue_date = datetime.strptime(data.get('issue_date'), '%Y-%m-%d').date()
        
        if data.get('expiry_date'):
            permit.expiry_date = datetime.strptime(data.get('expiry_date'), '%Y-%m-%d').date()
        
        permit.amount_paid = int(data.get('amount_paid', 0))
        permit.or_no = data.get('or_no')
        permit.issued_at = data.get('issued_at')
        permit.mayor = data.get('mayor')
        permit.quarter = data.get('quarter')
        permit.status = data.get('status')
        
        # Save the updated permit
        permit.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Permit updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    


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
                messages.success(request, f'Welcome back, {admin.full_name}!')
                return redirect('dashboard')
        except Admin.DoesNotExist:
            pass

        # If we reach here, login failed
        messages.error(request, 'Invalid username or password.')

    content = {'exclude_layout': True}
    return render(request, 'myapp/login.html', content)

def dashboard(request):
    permit_count = MayorsPermit.objects.count()  # total number of permits
    
    return render(request, 'myapp/dashboard.html', {
        'permit_count': permit_count
    })



@superadmin_required
def admin_management(request):
    admins = Admin.objects.all().select_related('created_by').order_by('-created_at')
    
    context = {
        'admins': admins,
    }
    return render(request, 'myapp/admin-management.html', context)

def add_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if Admin.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif Admin.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            hashed_password = make_password(password)
            Admin.objects.create(
                username=username,
                full_name=full_name,
                email=email,
                password=hashed_password
            )
            messages.success(request, "Admin created successfully!")
            return redirect('dashboard')  # redirect to same page or change as needed

    return render(request, "myapp/add-admin.html")


def admin_list(request):
   
    return render(request, 'myapp/admin-list.html')

def admin_logout(request):
    """Clear admin and superadmin session and redirect to login."""
    
    # Clear all session keys used in login
    session_keys = ['admin_id', 'superadmin_id', 'user_type', 'username', 'full_name']
    
    for key in session_keys:
        if key in request.session:
            del request.session[key]
    
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def mayors_permit(request):
    permits = MayorsPermit.objects.all()
    return render(request, 'myapp/mayors-permit.html', {'permits': permits})


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
        
        # Check for uniqueness
        if MayorsPermit.objects.filter(control_no=control_no).exists():
            messages.error(request, f"Control No '{control_no}' is already used.")
            return redirect('add-mayors-permit')

        if MayorsPermit.objects.filter(or_no=or_no).exists():
            messages.error(request, f"OR No '{or_no}' is already used.")
            return redirect('add-mayors-permit')

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
        return redirect('mayors-permit')  # redirect to permit list or change as needed

    return render(request, "myapp/add-mayors-permit.html")


def id_cards(request):
    cards = IDCard.objects.all()
    return render(request, 'myapp/id-cards.html', {'cards': cards})

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
        image = request.FILES.get("image")

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
            image=image,
        )

        messages.success(request, "ID Card added successfully!")
        return JsonResponse({"success": True})

    return JsonResponse({"success": False})

def update_mayors_permit(request, permit_id):

    permit = get_object_or_404(MayorsPermit, id=permit_id)

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

def mtop_print(request, pk):
    mtop = Mtop.objects.get(pk=pk)
    return render(request, 'myapp/mtop-print.html', {'mtop': mtop})

def franchise(request):
    franchises = Franchise.objects.all().order_by('-date')  # latest first
    return render(request, 'myapp/franchise.html', {'franchises': franchises}) 


def franchise_print(request, pk):
    franchise = get_object_or_404(Franchise, pk=pk)
    return render(request, "myapp/franchise-print.html", {"franchise": franchise})



def mayors_permit_tricycle(request):
    permits = MayorsPermitTricycle.objects.all()
    return render(request, 'myapp/mayors-permit-tri.html', {'permits': permits})



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
    # Create response as CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mayors_permit.csv"'

    writer = csv.writer(response)

    # CSV Header
    writer.writerow([
        'control_no',
        'name',
        'address',
        'motorized_operation',
        'business_name',
        'expiry_date',
        'amount_paid',
        'or_no',
        'issue_date',
        'issued_at',
        'mayor',
        'quarter',
        'status'
    ])

    # CSV Rows
    for p in MayorsPermit.objects.all():
        writer.writerow([
            p.control_no,
            p.name,
            p.address,
            p.motorized_operation,
            p.business_name,
            p.expiry_date,
            p.amount_paid,
            p.or_no,
            p.issue_date,
            p.issued_at,
            p.mayor,
            p.quarter,
            p.status,
        ])

    return response



def import_mayors_permit(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "No file uploaded.")
            return redirect("mayors-permit")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a CSV file.")
            return redirect("mayors-permit")

        errors = []
        success_count = 0

        try:
            file_data = csv_file.read().decode("utf-8").splitlines()
            reader = csv.reader(file_data)
            header = next(reader)  # Skip header row

            for i, row in enumerate(reader, start=2):  # start=2 to match CSV line numbers
                if len(row) != 13:
                    errors.append(f"Row {i}: Incorrect number of columns ({len(row)}).")
                    continue

                try:
                    # Validate and parse dates
                    issue_date = datetime.strptime(row[8], "%Y-%m-%d").date()
                    expiry_date = datetime.strptime(row[5], "%Y-%m-%d").date()

                    # Convert amount_paid to integer
                    amount_paid = int(row[6])

                    # Update existing or create new permit
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
                # Combine all row errors into one message
                messages.warning(request, "Some rows could not be imported:\n" + "\n".join(errors))

        except Exception as e:
            messages.error(request, f"Failed to read CSV file: {e}")

        return redirect("mayors-permit")


def sample_print(request):
    return render(request, 'myapp/sample-print.html')

def mayors_permit_history(request):
    return render(request, 'myapp/mayors-permit-history.html')
