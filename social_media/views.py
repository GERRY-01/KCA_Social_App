from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Profile, CompleteProfile, Post, Comments, Resource, Event, AdminProfile, Announcement, AnnouncementLike, Follow
import random
import calendar
from datetime import datetime
from django.core.paginator import Paginator
from django.utils import timezone

# Create your views here.
@login_required
def home(request):
    # Handle regular user profile (may not exist for admins)
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = None
    
    try:
        complete_profile = CompleteProfile.objects.get(user=request.user)
    except CompleteProfile.DoesNotExist:
        complete_profile = None

    posts = Post.objects.all().order_by('-created_at')
    
    # Get all users except current user
    all_users = User.objects.exclude(id=request.user.id)
    
    # Get users that the current user has any relationship with (accepted or pending)
    following = Follow.objects.filter(
        follower=request.user
    ).values_list('followed_id', flat=True)
    
    # Get status of each follow for more detailed display
    follow_status = {}
    for follow in Follow.objects.filter(follower=request.user):
        follow_status[follow.followed_id] = follow.status
    
    # ADD THIS LINE - Attach follow status to each post
    for post in posts:
        post.follow_status = follow_status.get(post.user.id, None)
    
    # Get pending follow requests for the current user
    pending_requests = Follow.objects.filter(
        followed=request.user,
        status='pending'
    ).select_related('follower')
    
    # Get follower counts for each user (accepted only)
    follower_counts = {}
    for user in all_users:
        follower_counts[user.id] = Follow.objects.filter(
            followed=user,
            status='accepted'
        ).count()
    
    # Get suggested users (users not followed yet and not pending)
    if all_users.exists():
        # Exclude users with pending requests
        pending_user_ids = pending_requests.values_list('follower_id', flat=True)
        suggested_users_list = all_users.exclude(
            id__in=following
        ).exclude(
            id__in=pending_user_ids
        )
        
        if suggested_users_list.exists():
            sample_size = min(3, suggested_users_list.count())
            suggested_users = random.sample(list(suggested_users_list), sample_size)
        else:
            suggested_users = []
    else:
        suggested_users = []
    
    all_suggestions = all_users

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'complete_profile': complete_profile,
        'posts': posts,
        'suggested_users': suggested_users,
        'all_suggestions': all_suggestions,
        'following': following,
        'follow_status': follow_status,
        'follower_counts': follower_counts,
        'pending_requests': pending_requests,
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
            # Redirect admin to admin dashboard, regular users to home
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
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
            return redirect('home')
        
        post = Post(user=user, caption=caption, media=media)
        post.save()

        messages.success(request, 'Post created successfully')

        return redirect('home')
    return redirect('home')

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
    
    # Get followers and following counts
    followers_count = Follow.objects.filter(followed=request.user).count()
    following_count = Follow.objects.filter(follower=request.user).count()
    
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'complete_profile': complete_profile,
        'user': request.user,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
    })

@login_required
def user_profile(request, user_id):
    """View another user's profile"""
    profile_user = get_object_or_404(User, id=user_id)
    
    try:
        user_profile = Profile.objects.get(user=profile_user)
    except Profile.DoesNotExist:
        user_profile = None
    
    try:
        complete_profile = CompleteProfile.objects.get(user=profile_user)
    except CompleteProfile.DoesNotExist:
        complete_profile = None

    posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    
    # Get followers and following counts
    followers_count = Follow.objects.filter(followed=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    
    # Check if current user follows this profile
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            followed=profile_user
        ).exists()
    
    return render(request, 'user_profile.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'complete_profile': complete_profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
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
    
    # Get users that the current user is following
    following = Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)
    
    # Get follower counts
    follower_counts = {}
    for user in all_users:
        follower_counts[user.id] = Follow.objects.filter(followed=user).count()
    
    # Paginate results (show 10 per page)
    paginator = Paginator(all_users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'suggestions.html', {
        'page_obj': page_obj,
        'user': request.user,
        'following': following,
        'follower_counts': follower_counts,
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
    
    # GET request - fetch and display resources with filter
    else:
        # Get filter parameter from URL
        filter_type = request.GET.get('filter', 'all')
        
        # Base queryset
        resources_list = Resource.objects.all().order_by('-uploaded_at')
        
        # Apply filter if needed
        if filter_type == 'my_uploads':
            resources_list = resources_list.filter(uploaded_by=request.user)
        
        # Get user's complete profile for the sidebar
        try:
            complete_profile = CompleteProfile.objects.get(user=request.user)
        except CompleteProfile.DoesNotExist:
            complete_profile = None
        
        # Get resources uploaded by the current user
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
            'resources': resources_list,
            'complete_profile': complete_profile,
            'my_uploads': my_uploads,
            'my_uploads_count': my_uploads_count,
            'total_resources': total_resources,
            'category_counts': category_counts,
            'current_filter': filter_type,
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
        events_list = Event.objects.filter(date__gte=timezone.now().date()).order_by('date', 'time')
        
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
            'events': events_list,
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
    
@login_required
def announcements(request):
    # Handle POST request - saving new announcement (only admins can post)
    if request.method == 'POST':
        # Check if user is admin before allowing post
        if not request.user.is_staff:
            messages.error(request, 'Only administrators can post announcements.')
            return redirect('announcements')
            
        # Get data from the form
        title = request.POST.get('title')
        content = request.POST.get('content')
        link = request.POST.get('link')
        image = request.FILES.get('image')
        
        # Validate required fields
        if not title or not content:
            messages.error(request, 'Title and content are required')
            return redirect('announcements')
        
        # Create new announcement
        announcement = Announcement(
            title=title,
            content=content,
            link=link,
            image=image,
            created_by=request.user
        )
        announcement.save()
        
        messages.success(request, 'Announcement posted successfully!')
        return redirect('announcements')
    
    # GET request - fetch and display announcements (everyone can view)
    else:
        # Get all announcements ordered by most recent
        announcements_list = Announcement.objects.all().order_by('-created_at')
        
        # Get user's complete profile for the sidebar
        try:
            complete_profile = CompleteProfile.objects.get(user=request.user)
        except CompleteProfile.DoesNotExist:
            complete_profile = None
        
        # Check which announcements the current user has liked
        user_likes = {}
        if request.user.is_authenticated:
            liked_announcements = AnnouncementLike.objects.filter(
                user=request.user
            ).values_list('announcement_id', flat=True)
            user_likes = {ann_id: True for ann_id in liked_announcements}
        
        context = {
            'announcements': announcements_list,
            'complete_profile': complete_profile,
            'user_likes': user_likes,
        }
        
        return render(request, 'announcements.html', context)

@login_required
def like_announcement(request, announcement_id):
    """Handle liking/unliking an announcement"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    # Check if user already liked this announcement
    like_exists = AnnouncementLike.objects.filter(
        announcement=announcement,
        user=request.user
    ).exists()
    
    if like_exists:
        # Unlike
        AnnouncementLike.objects.filter(
            announcement=announcement,
            user=request.user
        ).delete()
        announcement.likes -= 1
        announcement.save()
        messages.success(request, 'Announcement unliked')
    else:
        # Like
        AnnouncementLike.objects.create(
            announcement=announcement,
            user=request.user
        )
        announcement.likes += 1
        announcement.save()
        messages.success(request, 'Announcement liked')
    
    return redirect('announcements')

@login_required
def delete_announcement(request, announcement_id):
    """Delete an announcement (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('announcements')
    
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    # Check if the current user is the creator or superuser
    if request.user != announcement.created_by and not request.user.is_superuser:
        messages.error(request, 'You can only delete your own announcements')
        return redirect('announcements')
    
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully')
    
    return redirect('announcements')

@login_required
def edit_announcement(request, announcement_id):
    """Edit an announcement (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('announcements')
    
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    # Check if the current user is the creator or superuser
    if request.user != announcement.created_by and not request.user.is_superuser:
        messages.error(request, 'You can only edit your own announcements')
        return redirect('announcements')
    
    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.content = request.POST.get('content')
        announcement.link = request.POST.get('link')
        
        # Handle image update
        if request.FILES.get('image'):
            announcement.image = request.FILES.get('image')
        
        announcement.save()
        messages.success(request, 'Announcement updated successfully')
        return redirect('announcements')
    
    # GET request - show edit form
    context = {
        'announcement': announcement,
    }
    return render(request, 'edit_announcement.html', context)

def admin_signup(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        staff_id = request.POST.get('staff_id')
        department = request.POST.get('department')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')
        
        # Basic validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('admin_signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('admin_signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('admin_signup')
        
        if AdminProfile.objects.filter(staff_id=staff_id).exists():
            messages.error(request, 'Staff ID already exists')
            return redirect('admin_signup')
        
        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Mark as staff (admin)
        user.is_staff = True
        user.save()
        
        # Create AdminProfile
        admin_profile = AdminProfile(
            user=user,
            staff_id=staff_id,
            department=department
        )
        
        if profile_picture:
            admin_profile.profile_picture = profile_picture
        
        admin_profile.save()
        
        messages.success(request, 'Admin account created successfully! Please login.')
        return redirect('admin_login')
    
    # GET request - show the form
    return render(request, 'admin_signup.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:  # Check if user is staff/admin
            auth_login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('admin_dashboard')  
        else:
            messages.error(request, 'Invalid credentials or not an admin')
            return redirect('admin_login')
    
    return render(request, 'admin_login.html')

@login_required
def admin_dashboard(request):
    # Check if user is admin/staff
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('home')
    
    # Get statistics for the dashboard
    total_announcements = Announcement.objects.count()
    total_events = Event.objects.count()
    total_resources = Resource.objects.count()
    total_users = User.objects.count()
    
    # Get recent announcements
    recent_announcements = Announcement.objects.all().order_by('-created_at')[:5]
    
    # Get user's admin profile
    try:
        admin_profile = AdminProfile.objects.get(user=request.user)
    except AdminProfile.DoesNotExist:
        admin_profile = None
    
    context = {
        'announcements': recent_announcements,
        'total_announcements': total_announcements,
        'total_events': total_events,
        'total_resources': total_resources,
        'total_users': total_users,
        'admin_profile': admin_profile,
        'user': request.user,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def follow_user(request, user_id):
    """Follow a user - creates a pending request"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    # Don't allow following yourself
    if request.user == user_to_follow:
        messages.error(request, "You cannot follow yourself")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Check if there's an existing follow relationship
    existing_follow = Follow.objects.filter(
        follower=request.user,
        followed=user_to_follow
    ).first()
    
    if existing_follow:
        if existing_follow.status == 'pending':
            messages.info(request, f"Follow request already sent to {user_to_follow.get_full_name()}")
        elif existing_follow.status == 'accepted':
            messages.info(request, f"You already follow {user_to_follow.get_full_name()}")
        else:  # declined - create new request
            existing_follow.status = 'pending'
            existing_follow.save()
            messages.success(request, f"Follow request sent to {user_to_follow.get_full_name()}")
    else:
        # Create new follow request with pending status
        Follow.objects.create(
            follower=request.user,
            followed=user_to_follow,
            status='pending'
        )
        messages.success(request, f"Follow request sent to {user_to_follow.get_full_name()}")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def unfollow_user(request, user_id):
    """Unfollow a user (only works for accepted follows)"""
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    follow = Follow.objects.filter(
        follower=request.user,
        followed=user_to_unfollow,
        status='accepted'
    ).first()
    
    if follow:
        follow.delete()
        messages.success(request, f"You have unfollowed {user_to_unfollow.get_full_name()}")
    else:
        messages.error(request, "You don't follow this user")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def accept_follow(request, user_id):
    """Accept a follow request and follow back"""
    requester = get_object_or_404(User, id=user_id)
    
    # Get the pending follow request
    follow_request = get_object_or_404(
        Follow, 
        follower=requester, 
        followed=request.user,
        status='pending'
    )
    
    # Accept the request
    follow_request.status = 'accepted'
    follow_request.save()
    
    # Automatically follow back
    reverse_follow, created = Follow.objects.get_or_create(
        follower=request.user,
        followed=requester,
        defaults={'status': 'accepted'}
    )
    
    if created:
        messages.success(request, f"You are now following {requester.get_full_name()} back")
    else:
        if reverse_follow.status != 'accepted':
            reverse_follow.status = 'accepted'
            reverse_follow.save()
        messages.success(request, f"You are now following {requester.get_full_name()} back")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def decline_follow(request, user_id):
    """Decline a follow request"""
    requester = get_object_or_404(User, id=user_id)
    
    # Get the pending follow request
    follow_request = get_object_or_404(
        Follow, 
        follower=requester, 
        followed=request.user,
        status='pending'
    )
    
    # Decline the request
    follow_request.status = 'declined'
    follow_request.save()
    
    messages.info(request, f"Follow request from {requester.get_full_name()} declined")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def get_follow_requests(request):
    """Get all pending follow requests for the current user"""
    pending_requests = Follow.objects.filter(
        followed=request.user,
        status='pending'
    ).select_related('follower')
    
    return pending_requests