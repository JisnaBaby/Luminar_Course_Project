from django.db import models
from django.utils.timezone import now

class RegisterDB(models.Model):
    username = models.CharField(max_length=150, unique=True,null=False,blank=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords using make_password
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Add this
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    warning_count = models.IntegerField(default=0)# Add this

    def __str__(self):
        return self.username


class QuizParticipant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name

class QuizSubmission(models.Model):
    participant = models.ForeignKey(QuizParticipant, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.participant.name} - {self.score}"

class Post(models.Model):
    user = models.ForeignKey(RegisterDB, on_delete=models.CASCADE)
    caption = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(RegisterDB, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(RegisterDB, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ComplaintdB(models.Model):
    Comp_Name=models.CharField(max_length=100,blank=True,null=True)
    Comp_Email=models.CharField(max_length=100,blank=True,null=True)
    Comp_Mobile=models.CharField(max_length=100,blank=True,null=True)
    Comp_Subject=models.CharField(max_length=100,blank=True,null=True)
    Comp_Proof=models.FileField(upload_to="Complaint Proofs",blank=True,null=True)
    Comp_Details=models.TextField(max_length=1000,null=True,blank=True)

class UserProfile(models.Model):
    user = models.OneToOneField('RegisterDB', on_delete=models.CASCADE)  # Assuming custom user model
    bio = models.TextField(blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)

    def __str__(self):
        return self.user.username
class Message(models.Model):
    sender = models.ForeignKey(RegisterDB, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(RegisterDB, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.content[:20]}"

    class Meta:
        ordering = ['-timestamp']  # Latest messages first

class ContactdB(models.Model):
    Full_Name = models.CharField(max_length=100,null=True,blank=True)
    Mobile_Number = models.IntegerField(null=True,blank=True)
    Email = models.EmailField(max_length=100,null=True,blank=True)
    Subject = models.CharField(max_length=100,null=True,blank=True)
    Msg = models.CharField(max_length=500,null=True,blank=True)