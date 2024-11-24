import sys
import os
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from dotenv import load_dotenv
from django.contrib import messages
from .models import CustomUser


sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables first
load_dotenv()

# Configure the API key after loading the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# This part should be inside the view function to ensure a fresh chat instance for each request
def get_gemini_response(question):
    model = genai.GenerativeModel("gemini-pro")
    chat_instance = model.start_chat(history=[])  # New instance per request
    response = chat_instance.send_message(question, stream=True)
    return response

def home(request):
    # Initialize chat history in session if it doesn't exist
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    if request.method == "POST":
        genre = request.POST.get("genre")
        age = request.POST.get('ageGroup')
        language = request.POST.get('language')

        if genre and age and language:
            # Get the Gemini response
            message = f'Recommend me some movies of {genre} genre for {age} year olds in {language}. Give me the movie names only, nothing else. Separate each movie name with a ~'

            response = get_gemini_response(message)

            # Store user query and bot response in session
            request.session['chat_history'].append(("You", message))

            # Ensure response is iterable and properly formatted
            bot_response = "".join([chunk.text for chunk in response])

            # Split the response into a list of movies
            movies_list = bot_response.split('~')

            # Clean up the movie names by stripping any extra spaces
            movies = [movie.strip() for movie in movies_list if movie.strip()]

            # Store the formatted movie list in chat history
            request.session['chat_history'].append(("Bot", movies))

            # Ensure session is saved
            request.session.modified = True

    # Render the Q&A page with chat history
    return render(request, 'movie_recommender/index.html', {
        'chat_history': request.session['chat_history']
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')

        # Basic validation
        if password != password_confirmation:
            messages.error(request, "Passwords don't match.")
            return redirect('register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        # Create new user
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # Automatically log the user in after registration
        messages.success(request, "Registration successful.")
        return redirect('home')
    
    return render(request, 'movie_recommender/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user using the custom user model
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'movie_recommender/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')