from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return self.user.username
    

class CompleteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    CAMPUS_CHOICES = [
        ('main', 'Main Campus'),
        ('town', 'Town Campus'),
        ('kitengela', 'Kitengela Campus'),
        ('western', 'Western Campus'),
    ]
    campus = models.CharField(max_length=20, choices=CAMPUS_CHOICES)
    FACULTY_CHOICES = [
        ('computing', 'Faculty of Computing & Information Management'),
        ('business', 'School of Business'),
        ('education', 'School of Education'),
        ('arts', 'School of Arts & Social Sciences'),
        
    ]
    faculty = models.CharField(max_length=50, choices=FACULTY_CHOICES)
    PROGRAM_CHOICES = [
    ('bsd', 'Bachelor of Science in Data Science (BSD)'),
    ('bbit', 'Bachelor of Business Information Technology (BBIT)'),
    ('bisf', 'Bachelor of Information Security & Forensics (BISF)'),
    ('bac', 'Bachelor of Applied Communication (BAC)'),
    ('bcom', 'Bachelor of Commerce (BCom)'),
    ('procurement', 'Bachelor of Procurement and Logistics'),
    ('education', 'Bachelor of Education'),
    ('psychology', 'Bachelor of Arts in Counselling Psychology'),
    ]
    program = models.CharField(max_length=50, choices=PROGRAM_CHOICES)
    YEAR_CHOICES = [
    ('1', 'Year 1'),
    ('2', 'Year 2'),
    ('3', 'Year 3'),
    ('4', 'Year 4'),
    ('5', 'Year 5+'),
    ('na', 'N/A'),
    ]
    year = models.CharField(max_length=20, choices=YEAR_CHOICES)
    bio = models.TextField(max_length=150, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField()
    media = models.FileField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"
    
class Resource(models.Model):
    # Resource Categories
    CATEGORY_CHOICES = [
        ('notes', '📝 Notes'),
        ('past_papers', '📄 Past Papers'),
        ('textbooks', '📚 Textbooks'),
        ('tutorials', '🎥 Video Tutorials'),
        ('projects', '💻 Projects'),
        ('research', '🔬 Research Papers'),
    ]
    
    # File Types
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('excel', 'Excel'),
        ('video', 'Video'),
        ('link', 'Link'),
        ('zip', 'Zip'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    
    # File Upload or External Link
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resources')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Just track downloads (useful to see popular resources)
    downloads = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title


# Add this to your existing models.py

class Event(models.Model):
    # Event Categories
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('social', 'Social'),
        ('sports', 'Sports'),
        ('career', 'Career'),
        ('cultural', 'Cultural'),
        ('workshop', 'Workshop'),
        ('club', 'Club'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, help_text="Where the event is happening")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='social')
    event_link = models.URLField(blank=True, null=True, help_text="Link for registration or more info")
    
    # Date and Time 
    date = models.DateField(help_text="When is the event?")
    time = models.TimeField(help_text="What time does it start?")
    
    # Organizer
    organized_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    
    # Timestamps (when the event was created in the system)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"{self.title} - {self.date}"