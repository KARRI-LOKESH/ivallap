import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from cloudinary.models import CloudinaryField

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, age, phone, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        username = email.split("@")[0]
        user = self.model(
            email=email,
            name=name,
            age=age,
            phone=phone,
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, age, phone, password=None):
        user = self.create_user(email, name, age, phone, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    is_private = models.BooleanField(default=False) 
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    profile_pic = CloudinaryField('image',null=True, blank=True, default='default-profile_cymv7l')
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    firebase_uid = models.CharField(max_length=50, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'age', 'phone']

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return self.email
class FollowRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='sent_follow_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='received_follow_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({'Accepted' if self.is_accepted else 'Pending'})"
