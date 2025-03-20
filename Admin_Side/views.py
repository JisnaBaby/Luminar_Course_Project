from django.shortcuts import render,redirect
from Web_Side.models import RegisterDB,ComplaintdB,ContactdB
from django.http import JsonResponse
from django.contrib import messages
from .models import AdminRegister

# Create your views here.
def admin_login_page(request):
    return render(request, "Admin_login.html")


def admin_login(request):
    if request.method == "POST":
        l_name = request.POST.get('lo_mail')
        l_pwd = request.POST.get('lo_pass')

        try:
            user = AdminRegister.objects.get(email=l_name, password=l_pwd)
            request.session['user_id'] = user.id  # Store user ID in session
            request.session['Username'] = user.email
            messages.success(request, "Login successful! Welcome, Admin.")
            return redirect('indexpage')
        except AdminRegister.DoesNotExist:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect(admin_login_page)  # Redirect back to login page

    return redirect(admin_login_page)




def admin_reg_page(request):
    return render(request, "Admin_Reg.html")


def admin_reg_save(request):
    if request.method == "POST":
        mail = request.POST.get('reg_mail')
        pwd = request.POST.get('reg_pass')
        obj = AdminRegister(email=mail,password=pwd)
        obj.save()
        messages.success(request, "Thank you for joining us...... Have a nice day..")
        return redirect(admin_reg_page)


def indexpage(request):
    return render(request,"index.html")
def display_user(request):
    data = RegisterDB.objects.all()
    return render(request,"Display_User.html",{'data':data})

def display_complaint(request):
    data = ComplaintdB.objects.all()
    return render(request,"Display_Complaint.html",{'data':data})

def display_contact(request):
    data = ContactdB.objects.all()
    return render(request,"Contact.html",{'data':data})


def warned_users_page(request, count):
    users_got_warning = RegisterDB.objects.filter(warning_count=count)

    # Get the list of users who will be deleted before deletion
    warned_users = list(RegisterDB.objects.filter(warning_count__gte=5).values('id', 'username', 'email', 'warning_count'))

    # Delete users with warning_count >= 5
    RegisterDB.objects.filter(warning_count__gte=5).delete()

    if warned_users:
        return JsonResponse({'message': 'Users deleted due to repeated cyberbullying offenses', 'deleted_users': warned_users}, status=403)

    return render(request, "Warned_Users.html", {'warned_users': warned_users, 'users_got_warning': users_got_warning})

def delete_user(request, u_id):
    user = RegisterDB.objects.filter(id=u_id).first()

    if user:
        user.delete()
        messages.success(request, "User deleted successfully.")
    else:
        messages.error(request, "User not found.")

    return redirect('display_user')