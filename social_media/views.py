from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Profile, CompleteProfile

# Create your views here.
@login_required
def home(request):
    
    user_profile = Profile.objects.get(user=request.user)
    try :
        complete_profile = CompleteProfile.objects.get(user=request.user)
    except CompleteProfile.DoesNotExist:
        complete_profile = None

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'complete_profile': complete_profile,
    }
    return render(request, 'home.html', context)

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        id_number = request.POST.get('idNumber')
        username = request.POST.get('username')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')
        
        if Profile.objects.filter(id_number=id_number).exists():
            messages.error(request, 'ID number already exists')
            return redirect('signup')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile = Profile(user=user, id_number=id_number, role=role)
        profile.save()
        
        auth_login(request, user)
        return redirect('complete_profile')

    return render(request, 'signup.html')

@login_required
def complete_profile(request):
    if request.method == 'POST':
        campus = request.POST.get("campus")
        faculty = request.POST.get("faculty")
        program = request.POST.get("program")
        year = request.POST.get("year")
        bio = request.POST.get("bio")

         # Optional: handle profile picture if added
        profile_picture = request.FILES.get("profilePicture")

        profile, created = CompleteProfile.objects.get_or_create(user=request.user)
        profile.campus = campus
        profile.faculty = faculty
        profile.program = program
        profile.year = year
        profile.bio = bio

        if profile_picture:
            profile.profile_picture = profile_picture

        profile.save()
        messages.success(request, 'Profile completed successfully')
        return redirect('home')
    return render(request, 'complete_profile.html')

def login(request):
    return render(request, 'login.html')