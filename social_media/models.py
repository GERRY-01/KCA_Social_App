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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField()
    media = models.FileField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)