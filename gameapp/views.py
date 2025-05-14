from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import datetime
from .db import high_scores_collection, users_collection  # MongoDB collection
from django.contrib.auth.forms import AuthenticationForm

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()  # Automatically hashes password

            # Get extra fields from POST
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')

            # Update Django user model with extra info
            user.first_name = firstname
            user.last_name = lastname
            user.email = email
            user.save()

            # Save additional user details to MongoDB
            users_collection.insert_one({
                'username': user.username,
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'mobile': mobile,
                'signup_date': datetime.datetime.now()
            })

            login(request, user)
            # Redirect to login page after successful signup
            return redirect('/login/?next=/scores/&signup=success')

        else:
            return render(request, 'signup.html', {'form': form, 'error': "Signup error. Try again."})
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

@login_required
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', '/scores/'))
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials. Please try again.'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def user_scores(request):
    # Fetch scores
    scores = list(high_scores_collection.find({'username': request.user.username}))
    for s in scores:
        s['_id'] = str(s['_id'])
        s['date'] = s.get('date', 'N/A')
        if isinstance(s['date'], datetime.datetime):
            s['date'] = s['date'].strftime('%Y-%m-%d %H:%M')
        s['moves'] = s.get('moves', 'N/A')
        s['time_taken'] = s.get('time_taken', 'N/A')

    # Fetch user info
    user_info = users_collection.find_one({'username': request.user.username})
    if user_info:
        user_info.pop('_id', None)
        if 'signup_date' in user_info and isinstance(user_info['signup_date'], datetime.datetime):
            user_info['signup_date'] = user_info['signup_date'].strftime('%Y-%m-%d')

    return render(request, 'scores.html', {'scores': scores, 'user_info': user_info})

@login_required
def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Debugging line
            
            moves = data.get('moves')
            time_taken = data.get('time_taken')

            print(f"Received moves: {moves}, time_taken: {time_taken}")  # Debugging line

            if moves is not None and time_taken is not None:
                # Save the score to MongoDB
                high_scores_collection.insert_one({
                    'username': request.user.username,
                    'moves': int(moves),
                    'time_taken': int(time_taken),
                    'date': datetime.datetime.now()
                })

                return JsonResponse({'status': 'success'}, status=201)
            else:
                return JsonResponse({'error': 'Missing moves or time_taken in request body'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Failed to parse request body'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

      

   



def memory_game(request):
    return render(request, 'index.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'  # Use the appropriate template

@csrf_exempt  # if you're not using CSRF token; remove if token is used
@login_required
@require_POST
def save_after_login(request):
    try:
        data = json.loads(request.body)
        moves = int(data.get('moves', 0))
        time = float(data.get('time', 0))

        # Save the score in MongoDB with user info
        score_data = {
            'user_id': str(request.user.id),
            'username': request.user.username,
            'moves': moves,
            'time': time,
        }
        high_scores_collection.insert_one(score_data)

        return JsonResponse({'success': True, 'message': 'Score saved.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
