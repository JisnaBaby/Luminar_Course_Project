from django.shortcuts import render, redirect,get_object_or_404
from .models import QuizParticipant, QuizSubmission,RegisterDB,Post,Like,Comment,ComplaintdB,UserProfile,Message,ContactdB
from .forms import QuizRegistrationForm
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import JsonResponse
from django.conf import settings
import os
from django.contrib import messages
from .cyberbullying import load_model_and_predict
import json
from django.db.models import F,Q,Max
from django.utils import timezone
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def homepage(request):
    return render(request,"Home_page.html")
def user_login_page(request):
    return render(request,"User_Loginpage.html")
def login_view(request):
    if request.method == "POST":
        l_name = request.POST.get('lo_name')
        l_pwd = request.POST.get('lo_pass')

        try:
            # Check if the user exists in RegisterDB
            user = RegisterDB.objects.get(username=l_name, password=l_pwd)
            request.session['user_id'] = user.id  # Store user ID in session
            request.session['Username'] = user.username  # Store username in session
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('profile_page')
        except RegisterDB.DoesNotExist:
            messages.error(request, "No such user found. Check your username or password.")
            return redirect('user_login_page')

    return redirect('user_login_page')
def reg_page(request):
    return render(request,"User_Registrationpage.html")
def reg_save(request):
    if request.method =="POST":
        f_name=request.POST.get('reg_name')
        u_name=request.POST.get('reg_uname')
        mob=request.POST.get('reg_mob')
        mail=request.POST.get('reg_mail')
        pwd=request.POST.get('reg_pass')
        obj=RegisterDB(full_name=f_name,username=u_name,email=mail,phone=mob,password=pwd)
        obj.save()
        messages.success(request,"Thank you for joining us...... Have a nice day..")
        return redirect(reg_page)
def profile_page(request):
    if 'Username' not in request.session:
        return redirect('user_login_page')  # Redirect to login if not logged in

    username = request.session.get('Username')
    user = RegisterDB.objects.filter(username=username).first()

    if not user:
        messages.error(request, "User not found.")
        return redirect('user_login_page')

    # Fetch or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        bio = request.POST.get('bio')
        place = request.POST.get('place')
        gender = request.POST.get('gender')

        # Update user profile
        user_profile.bio = bio
        user_profile.place = place
        user_profile.gender = gender
        user_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile_page')

    posts = Post.objects.filter(user=user).order_by('-created_at')

    # Get all users except the logged-in user
    friends = RegisterDB.objects.exclude(id=user.id).exclude(username=None).exclude(username="")




    return render(request, "Profile_Page.html", {
        'user': user,
        'user_profile': user_profile,
        'posts': posts,
        'friends': friends,  # Passing the users list to template
    })
def cyber_course(request):
    return render(request,"Course.html")
def bullying_course(request):
    return render(request,"Cyber_Bullying.html")

def quiz_form(request):
    return render(request,"Quiz_form.html")

def quiz_reg(request):
    participant = None  # Initialize to avoid errors

    if request.method == "POST":
        form = QuizRegistrationForm(request.POST)
        if form.is_valid():
            participant = form.save()
            messages.success(request, "Quiz Registration succesfull!..")
            return redirect('quiz_form', participant_id=participant.id)  # Redirect to the quiz form

    else:
        form = QuizRegistrationForm()


    return render(request, 'Quiz_Registration.html', {'form': form, 'participant': participant})

ANSWER_KEY = {
    'q1': 'A', 'q2': 'B', 'q3': 'B', 'q4': 'C', 'q5': 'B',
    'q6': 'B', 'q7': 'B', 'q8': 'A', 'q9': 'B', 'q10': 'C',
    'q11': 'B', 'q12': 'C', 'q13': 'C', 'q14': 'B', 'q15': 'B',
    'q16': 'B', 'q17': 'C', 'q18': 'B', 'q19': 'C', 'q20': 'B',
    'q21': 'A', 'q22': 'B', 'q23': 'C', 'q24': 'A', 'q25': 'B',
    'q26': 'A', 'q27': 'A', 'q28': 'C', 'q29': 'A', 'q30': 'B'
}


# Register Participant
def register_quiz(request):
    if request.method == "POST":
        form = QuizRegistrationForm(request.POST)
        if form.is_valid():
            participant = form.save()
            messages.success(request,"Quiz Registration succesfull!..")
            return redirect('quiz_form', participant_id=participant.id)
    else:
        form = QuizRegistrationForm()
    return render(request, 'Quiz_registration.html', {'form': form})

# Quiz Form View
def quiz_form(request, participant_id):
    participant = QuizParticipant.objects.get(id=participant_id)
    return render(request, 'Quiz_form.html', {'participant': participant})

# Calculate Score
def submit_quiz(request, participant_id):
    participant = QuizParticipant.objects.get(id=participant_id)
    total_questions = len(ANSWER_KEY)  # Get total number of questions
    max_score = total_questions * 3  # Max possible score (assuming each correct answer is +3)

    # Count previous attempts
    total_attempts = QuizSubmission.objects.filter(participant=participant).count()

    if total_attempts >= 3:
        # If user has already failed 3 times, lock the quiz
        return render(request, 'Quiz_Result.html', {
            'participant': participant,
            'locked': True  # Send locked status to the template
        })

    if request.method == "POST":
        score = 0
        for question, correct_answer in ANSWER_KEY.items():
            user_answer = request.POST.get(question, '')  # Get submitted answer
            if user_answer:
                if user_answer == correct_answer:
                    score += 3  # Correct answer: +3 points
                else:
                    score -= 1  # Wrong answer: -1 point

        # Calculate percentage
        percentage = (score / max_score) * 100

        # Save attempt in database
        QuizSubmission.objects.create(participant=participant, score=score)

        # Check if the user failed (assuming pass mark is 40%)
        failed_attempts = QuizSubmission.objects.filter(participant=participant, score__lt=0.4 * max_score).count()

        return render(request, 'Quiz_Result.html', {
            'participant': participant,
            'score': score,
            'percentage': percentage,
            'attempts_left': max(0, 3 - total_attempts - 1),  # Show remaining attempts
            'locked': failed_attempts >= 3  # Lock after 3 failures
        })

    return redirect('Quiz_form', participant_id=participant.id)


def generate_certificate(request, participant_id):
    participant = QuizParticipant.objects.get(id=participant_id)

    # Retrieve the latest quiz submission for the participant
    submission = QuizSubmission.objects.filter(participant=participant).order_by('-id').first()

    template_path = 'Certificate.html'
    context = {
        'participant': participant,
        'score': submission.score if submission else 0,  # Ensure score is available
        'percentage': (submission.score / (len(ANSWER_KEY) * 3)) * 100 if submission else 0
    }

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{participant.name}_certificate.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


def upload_profile(request):
    if request.method == "POST" and request.FILES.get('profile_image'):
        username = request.session.get('Username')
        user = RegisterDB.objects.filter(username=username).first()

        if user:
            # Delete old profile image if it exists
            if user.profile_image:
                old_image_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_image))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Save new image
            user.profile_image = request.FILES['profile_image']
            user.save()

            return JsonResponse({'profile_image_url': user.profile_image.url})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def upload_cover(request):
    if request.method == "POST" and request.FILES.get('cover_photo'):
        username = request.session.get('Username')
        user = RegisterDB.objects.filter(username=username).first()

        if user:
            # Delete old cover photo if it exists
            if user.cover_photo:
                old_cover_path = os.path.join(settings.MEDIA_ROOT, str(user.cover_photo))
                if os.path.exists(old_cover_path):
                    os.remove(old_cover_path)

            # Save new cover photo
            user.cover_photo = request.FILES['cover_photo']
            user.save()

            return JsonResponse({'cover_photo_url': user.cover_photo.url})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def create_post(request):
    if request.method == "POST":
        user = RegisterDB.objects.filter(username=request.session.get('Username')).first()
        caption = request.POST.get('caption')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if not user:
            return JsonResponse({"error": "User not found"}, status=400)

        if not caption and not image and not video:
            return JsonResponse({"error": "Post cannot be empty"}, status=400)

        post = Post.objects.create(user=user, caption=caption, image=image, video=video)
        post.save()
        return redirect('profile_page')

    return JsonResponse({"error": "Invalid request"}, status=400)


def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    user = RegisterDB.objects.filter(username=request.session.get('Username')).first()

    like, created = Like.objects.get_or_create(post=post, user=user)
    if not created:
        like.delete()

    return JsonResponse({'like_count': post.like_set.count()})

def add_comment(request, post_id):
    if request.method == "POST":
        post = Post.objects.filter(id=post_id).first()
        if not post:
            return JsonResponse({'error': 'Post not found'}, status=404)

        user = RegisterDB.objects.filter(username=request.session.get('Username')).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=400)

        try:
            data = json.loads(request.body)
            comment_text = data.get('comment', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        if not comment_text:
            return JsonResponse({'error': 'Comment cannot be empty'}, status=400)

        # Detect cyberbullying
        bullying = load_model_and_predict("Web_Side/cyberbullying_model.pkl", "Web_Side/vectorizer.pkl", comment_text)
        print("Bullying Detection:", bullying)  # Debugging log

        if bullying == "Cyberbullying":
            warning_message = "Warning: Cyberbullying is a criminal offense"
            comment = Comment.objects.create(post=post, user=user, text=warning_message)
            comment.save()

            # Increment user's warning count
            user.warning_count = F('warning_count') + 1
            user.save()

            # Fetch updated user object
            user.refresh_from_db()

            # If warnings exceed 5, delete user account
            if user.warning_count >= 5:
                user.delete()
                return JsonResponse({'message': 'User account deleted due to repeated cyberbullying offenses'}, status=403)

            return JsonResponse({
                'comment_user': user.full_name if user.full_name else user.username,
                'comment_text': warning_message
            })

        # Save normal comments
        comment = Comment.objects.create(post=post, user=user, text=comment_text)
        comment.save()
        c_count = Comment.objects.filter(post_id=post_id).count()


        return JsonResponse({
            'comment_user': user.full_name if user.full_name else user.username,
            'comment_text': comment_text,
            'c_count':c_count
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)

import speech_recognition as sr
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from pydub import AudioSegment
from .models import Post, RegisterDB, Comment

from pydub import AudioSegment
from imageio_ffmpeg import get_ffmpeg_exe
from pydub import AudioSegment

from pydub import AudioSegment
from imageio_ffmpeg import get_ffmpeg_exe

# Get FFmpeg path
ffmpeg_path = get_ffmpeg_exe()

# Explicitly set paths for pydub
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffmpeg_path.replace("ffmpeg", "ffprobe")  # Ensure ffprobe is set

print("Using FFmpeg at:", ffmpeg_path)


def convert_to_wav(input_audio):
    """
    Converts an audio file to WAV format with PCM encoding (16kHz, mono) using ffmpeg-python.
    """
    try:
        output_wav = input_audio.rsplit('.', 1)[0] + ".wav"
        
        # Run FFmpeg command via Python
        (
            ffmpeg
            .input(input_audio)
            .output(output_wav, format="wav", acodec="pcm_s16le", ar="16000", ac="1")
            .run(overwrite_output=True)
        )

        return output_wav
    except Exception as e:
        print("Error converting audio to WAV:", e)
        return None

def speech_to_text(audio_path):
    """
    Converts speech to text from an audio file.
    """
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            extracted_text = recognizer.recognize_google(audio_data)  # Using Google Speech API
            print("Extracted text:", extracted_text)
            return extracted_text
    except sr.UnknownValueError:
        return ""  # Speech was not understood
    except sr.RequestError:
        return "Speech recognition service unavailable"
    except Exception as e:
        print("Speech recognition error:", e)
        return "Error processing audio"

@csrf_exempt
def add_audio_comment(request, post_id):
    """
    Handles adding an audio comment to a post.
    - Saves the uploaded audio file.
    - Converts to WAV if necessary.
    - Extracts text using speech recognition.
    - Detects cyberbullying.
    """
    if request.method == 'POST' and request.FILES.get('audio'):
        print("Audio file received:", request.FILES['audio'])

        try:
            post = Post.objects.get(id=post_id)
            user = RegisterDB.objects.filter(username=request.session.get('Username')).first()

            if not user:
                return JsonResponse({'success': False, 'error': 'User not found'})

            audio_file = request.FILES['audio']
            
            # Save the audio comment
            comment = Comment.objects.create(post=post, user=user, audio=audio_file)
            print("Comment created:", comment)

            # Get the saved audio file path
            audio_path = comment.audio.path
            if not os.path.exists(audio_path):
                print("Error: Audio file does not exist at path:", audio_path)
                return JsonResponse({'success': False, 'error': 'Audio file not found'})

            print("Audio file exists at:", audio_path)

            # Convert to WAV if needed
            if not audio_path.lower().endswith('.wav'):
                converted_audio_path = convert_to_wav(audio_path)
                if converted_audio_path:
                    audio_path = converted_audio_path
                else:
                    return JsonResponse({'success': False, 'error': 'Failed to convert audio file'})

            # Extract text from the audio
            extracted_text = speech_to_text(audio_path)
            print("Extracted text:", extracted_text)

            # Check for cyberbullying if text was extracted
            if extracted_text:
                bullying = load_model_and_predict("Web_Side/cyberbullying_model.pkl", 
                                                  "Web_Side/vectorizer.pkl", 
                                                  extracted_text)

                if bullying == "Cyberbullying":
                    warning_message = "Warning: Cyberbullying is a criminal offense"
                    comment.text = warning_message
                    comment.save()

                    # Increment user's warning count
                    user.warning_count = F('warning_count') + 1
                    user.save()
                    user.refresh_from_db()

                    # If warnings exceed 5, delete user account
                    if user.warning_count >= 5:
                        user.delete()
                        return JsonResponse({
                            'success': False,
                            'message': 'User account deleted due to repeated cyberbullying offenses'
                        }, status=403)

                    return JsonResponse({
                        'success': True,
                        'comment_user': user.full_name if user.full_name else user.username,
                        'comment_text': warning_message,
                        'is_cyberbullying': True
                    })

            # Save the extracted text to the comment
            comment.text = extracted_text if extracted_text else ""
            comment.save()

            # Count comments for the post
            c_count = Comment.objects.filter(post_id=post_id).count()

            return JsonResponse({
                'success': True,
                'comment_user': user.full_name if user.full_name else user.username,
                'audio_url': comment.audio.url,
                'c_count': c_count
            })

        except Exception as e:
            print("Exception:", e)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})



def complaint(request):
    return render(request, "Complaint.html")

def save_complaint(request):
    if request.method =="POST":
        c_nm=request.POST.get('c_name')
        c_em=request.POST.get('c_mail')
        c_phn=request.POST.get('c_mob')
        c_sec=request.POST.get('c_sub')
        c_det=request.POST.get('c_msg')
        c_pr=request.FILES['c_proof']
        obj=ComplaintdB(Comp_Name=c_nm,Comp_Email=c_em,Comp_Mobile=c_phn,
                        Comp_Subject=c_sec,Comp_Details=c_det,Comp_Proof=c_pr)
        obj.save()
        messages.success(request, "Complaint Saved Successfully... Our executives will contact you shortly!..")
        return redirect(complaint)
def user_profile(request, username):
    user = RegisterDB.objects.filter(username=username).first()

    if not user:
        messages.error(request, "User not found.")
        return redirect('profile_page')

    user_profile, created = UserProfile.objects.get_or_create(user=user)
    posts = Post.objects.filter(user=user).order_by('-created_at')

    return render(request, "User_Profile.html", {
        'user': user,
        'user_profile': user_profile,
        'posts': posts
    })

def logout(request):
    if request.method=="POST":
        request.session.flush()
        messages.success(request,"Logout Successfully...!")
    return redirect(user_login_page)


def chat_room(request, room_name):
    if 'Username' not in request.session:
        return redirect('user_login_page')  # Redirect to login if not logged in

    username = request.session.get('Username')
    current_user = RegisterDB.objects.filter(username=username).first()
    friend = RegisterDB.objects.get(username=room_name)

    if not current_user:
        return redirect('user_login_page')

    search_query = request.GET.get('search', '')

    # Get all users except the logged-in user
    users = RegisterDB.objects.exclude(id=current_user.id).exclude(username__isnull=True).exclude(username="")

    # Fetch chat messages related to the room
    chats = Message.objects.filter(
        (Q(sender=current_user) & Q(receiver__username=room_name)) |
        (Q(receiver=current_user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))

    chats = chats.order_by('timestamp')

    user_last_messages = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=current_user) & Q(receiver=user)) |
            (Q(receiver=current_user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Convert timestamps to timezone-aware before sorting
    def get_timestamp(msg):
        if msg and msg.timestamp:
            return timezone.make_aware(msg.timestamp) if timezone.is_naive(msg.timestamp) else msg.timestamp
        return timezone.make_aware(datetime.min)

    user_last_messages.sort(
        key=lambda x: get_timestamp(x['last_message']),
        reverse=True
    )

    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
        'current_user': current_user,
        'friend' : friend
    })

def save_contact(request):
    if request.method=="POST":
        fnm=request.POST.get('f_name')
        phn=request.POST.get('c_mob')
        em=request.POST.get('c_mail')
        sub=request.POST.get('c_sub')
        msg=request.POST.get('c_msg')
        obj=ContactdB(Full_Name=fnm,Mobile_Number=phn,Email=em,Subject=sub,Msg=msg)
        obj.save()
        messages.success(request,"Thank you for contacting us.. Our Executive will contact you shortly... Have a nice day!")
        return redirect(homepage)


