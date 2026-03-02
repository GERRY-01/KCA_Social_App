from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Profile, CompleteProfile, Post, Comments,Resource,Event
import random
import calendar
from datetime import datetime
from django.core.paginator import Paginator
from django.utils import timezone

# Create your views here.
@login_required
def home(request):
    
    user_profile = Profile.objects.get(user=request.user)
    try :
        complete_profile = CompleteProfile.objects.get(user=request.user)
    except CompleteProfile.DoesNotExist:
        complete_profile = None

    posts = Post.objects.all().order_by('-created_at')
    all_users = User.objects.exclude(id=request.user.id)
    suggested_users = random.sample(list(all_users), min(3, all_users.count()))
    all_suggestions = all_users

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'complete_profile': complete_profile,
        'posts': posts,
        'suggested_users': suggested_users,
        'all_suggestions': all_suggestions
    }
    return render(request, 'home.html', context)

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        id_number = request.POST.get('idNumber')
        username = request.POST.get('username')
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

        profile = Profile(user=user, id_number=id_number)
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
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def create_post(request):
    if request.method == 'POST':
        caption = request.POST.get('caption')
        media = request.FILES.get('media')
        user = request.user
        
        if not caption:
            messages.error(request, 'Caption is required')
            return render(request, 'home.html')
        
        post = Post(user=user, caption=caption, media=media)
        post.save()

        messages.success(request, 'Post created successfully')

        return redirect('home')
    return render(request, 'home.html')

def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')

def profile(request):
    # Get or create profile (similar to home view)
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = None
    
    try:
        complete_profile = CompleteProfile.objects.get(user=request.user)
    except CompleteProfile.DoesNotExist:
        complete_profile = None

    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'complete_profile': complete_profile,
        'user': request.user ,
        'posts': posts
    })

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment_text = request.POST.get('comment')
        
        if comment_text:  # Only create comment if not empty
            Comments.objects.create(
                post=post,
                user=request.user,
                comment=comment_text
            )
        
        # Redirect back to the referring page (where the comment came from)
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')


@login_required
def view_all_suggestions(request):
    # Get all users except current user
    all_users = User.objects.exclude(id=request.user.id)
    
    # Paginate results (show 10 per page)
    paginator = Paginator(all_users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'suggestions.html', {
        'page_obj': page_obj,
        'user': request.user
    })

@login_required
def resources(request):
    # Handle POST request - saving new resource
    if request.method == 'POST':
        # Get data from the form
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        file_type = request.POST.get('file_type')
        external_link = request.POST.get('external_link')
        
        # Handle file upload
        file = request.FILES.get('file')
        
        # Validate required fields
        if not title or not description or not category or not file_type:
            messages.error(request, 'Please fill in all required fields')
            return redirect('resources')
        
        # Create new resource instance
        resource = Resource(
            title=title,
            description=description,
            category=category,
            file_type=file_type,
            uploaded_by=request.user
        )
        
        # Set either file or external link based on file type
        if file_type == 'link':
            if not external_link:
                messages.error(request, 'Please provide an external link')
                return redirect('resources')
            resource.external_link = external_link
        else:
            if not file:
                messages.error(request, 'Please upload a file')
                return redirect('resources')
            resource.file = file
        
        # Save to database
        resource.save()
        
        messages.success(request, 'Resource shared successfully!')
        return redirect('resources')
    
    # GET request - fetch and display resources
    else:
        # Get all resources ordered by most recent
        resources = Resource.objects.all().order_by('-uploaded_at')
        
        # Get user's complete profile for the sidebar
        try:
            complete_profile = CompleteProfile.objects.get(user=request.user)
        except CompleteProfile.DoesNotExist:
            complete_profile = None
        
        # Get resources uploaded by the current user
        my_uploads = Resource.objects.filter(uploaded_by=request.user)
        my_uploads_count = my_uploads.count()
        
        # Get total resources count
        total_resources = Resource.objects.count()
        
        # Get category counts for the filter buttons
        category_counts = {}
        for category_code, category_name in Resource.CATEGORY_CHOICES:
            count = Resource.objects.filter(category=category_code).count()
            category_counts[category_code] = count
        
        context = {
            'resources': resources,
            'complete_profile': complete_profile,
            'my_uploads': my_uploads,
            'my_uploads_count': my_uploads_count,
            'total_resources': total_resources,
            'category_counts': category_counts,
        }
        
        return render(request, 'resources.html', context)


@login_required
def resources(request):
    # Get filter parameter from URL
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    resources = Resource.objects.all().order_by('-uploaded_at')
    
    # Apply filter if needed
    if filter_type == 'my_uploads':
        resources = resources.filter(uploaded_by=request.user)
    
    # Rest of your context remains the same
    try:
        complete_profile = CompleteProfile.objects.get(user=request.user)
    except CompleteProfile.DoesNotExist:
        complete_profile = None
    
    my_uploads = Resource.objects.filter(uploaded_by=request.user)
    my_uploads_count = my_uploads.count()
    total_resources = Resource.objects.count()
    
    # Category counts
    category_counts = {}
    for category_code, category_name in Resource.CATEGORY_CHOICES:
        safe_key = category_code.replace('-', '_')
        if filter_type == 'my_uploads':
            count = Resource.objects.filter(category=category_code, uploaded_by=request.user).count()
        else:
            count = Resource.objects.filter(category=category_code).count()
        category_counts[safe_key] = count
    
    context = {
        'resources': resources,
        'complete_profile': complete_profile,
        'my_uploads': my_uploads,
        'my_uploads_count': my_uploads_count,
        'total_resources': total_resources,
        'category_counts': category_counts,
        'current_filter': filter_type,  # Pass current filter to template
    }
    
    return render(request, 'resources.html', context)

def events(request):
    # Handle POST request - saving new event
    if request.method == 'POST':
        # Get data from the form
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        category = request.POST.get('category')
        event_link = request.POST.get('event_link')
        date = request.POST.get('date')
        time = request.POST.get('time')
        
        # Validate required fields
        if not title or not description or not location or not category or not date or not time:
            messages.error(request, 'Please fill in all required fields')
            return redirect('events')
        
        # Create new event instance
        event = Event(
            title=title,
            description=description,
            location=location,
            category=category,
            event_link=event_link,
            date=date,
            time=time,
            organized_by=request.user
        )
        
        # Save to database
        event.save()
        
        messages.success(request, 'Event created successfully!')
        return redirect('events')
    
    # GET request - fetch and display events
    else:
        # Get current month and year (default to current month)
        today = timezone.now().date()
        current_year = today.year
        current_month = today.month
        
        # Check if month is passed via GET parameters
        month_param = request.GET.get('month')
        year_param = request.GET.get('year')
        
        if month_param and year_param:
            try:
                current_month = int(month_param)
                current_year = int(year_param)
            except ValueError:
                pass
        
        # Get all upcoming events
        events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date', 'time')
        
        # Get events for the current month
        month_events = Event.objects.filter(
            date__year=current_year,
            date__month=current_month
        )
        
        # Create a list of dates that have events
        event_dates = [event.date.day for event in month_events]
        
        # Generate calendar data for the current month
        cal = calendar.monthcalendar(current_year, current_month)
        
        # Get month name
        month_name = datetime(current_year, current_month, 1).strftime('%B')
        
        # Previous and next month navigation
        prev_month = current_month - 1
        prev_year = current_year
        if prev_month == 0:
            prev_month = 12
            prev_year = current_year - 1
            
        next_month = current_month + 1
        next_year = current_year
        if next_month == 13:
            next_month = 1
            next_year = current_year + 1
        
        # Get past events (last 5)
        past_events = Event.objects.filter(date__lt=timezone.now().date()).order_by('-date', '-time')[:5]
        
        # Get user's complete profile for the sidebar
        try:
            complete_profile = CompleteProfile.objects.get(user=request.user)
        except CompleteProfile.DoesNotExist:
            complete_profile = None
        
        # Get events organized by the current user
        my_events = Event.objects.filter(organized_by=request.user)
        my_events_count = my_events.count()
        
        # Get total events count
        total_events = Event.objects.count()
        
        # Get upcoming events count (next 7 days)
        next_week = timezone.now().date() + timezone.timedelta(days=7)
        upcoming_week_count = Event.objects.filter(
            date__gte=timezone.now().date(),
            date__lte=next_week
        ).count()
        
        # Get category counts for filters
        category_counts = {}
        for category_code, category_name in Event.CATEGORY_CHOICES:
            count = Event.objects.filter(category=category_code, date__gte=timezone.now().date()).count()
            # Replace hyphens with underscores for safe template access
            safe_key = category_code.replace('-', '_')
            category_counts[safe_key] = count
        
        context = {
            'events': events,
            'past_events': past_events,
            'complete_profile': complete_profile,
            'my_events': my_events,
            'my_events_count': my_events_count,
            'total_events': total_events,
            'upcoming_week_count': upcoming_week_count,
            'category_counts': category_counts,
            'category_choices': Event.CATEGORY_CHOICES,
            # Calendar data
            'cal': cal,
            'current_month': current_month,
            'current_year': current_year,
            'month_name': month_name,
            'event_dates': event_dates,
            'today_day': today.day,
            'today_month': today.month,
            'today_year': today.year,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
        }
        
        return render(request, 'events.html', context)