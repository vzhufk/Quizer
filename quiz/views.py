import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render

# Create your views here.
from quiz import models, forms
from quiz.forms import ProfileEditForm, ProfilePasswordEditForm
from quiz.models import User, Quiz, Record


def start_user_session(request, user):
    """
    Starts user session
    :param request: HTTP request
    :param user: models.User instance
    :return: HTTP request with session
    """
    request.session['logged'] = True
    request.session['id'] = user.id
    request.session['username'] = user.username
    request.session['email'] = user.email
    return request


def end_user_session(request):
    """
    Ends session for user
    :param request: HTTP request with current session
    :return: HTTP request without session
    """
    request.session['logged'] = None
    request.session['id'] = None
    request.session['username'] = None
    request.session['email'] = None
    return request


def check_user_session(request):
    """
    Checks if client is logged in
    :param request: HTTP request
    :return:
    """
    try:
        request.session['logged']
    except KeyError:
        end_user_session(request)
    return request.session['logged'] is not None


def home(request, message=None):
    """
    Main page
    :param request: HTTP request
    :param message: Optional message, if you want ot redirect client with some message
    :return:
    """
    return render(request, 'quiz/home.html', {'message': message})


def run(request, current_id):
    """
    Quiz runner
    :param request: HTTP request
    :param current_id: selected quiz id
    :return:
    """
    if not check_user_session(request):
        return home(request, "To pass this test, you need to be resisted ;)")
    else:
        try:
            quiz = models.Quiz.objects.get(id=current_id)
            questions = models.Question.objects.filter(to=current_id)
            tasks = []
            for i in questions:
                current = {'question': i,
                           'answers': models.Answer.objects.filter(to=i.id)}
                tasks.append(current)
        except ObjectDoesNotExist:
            raise Http404

        if request.method == 'POST':
            answers = []
            for key in request.POST:
                if request.POST[key] == 'on':
                    answers.append(int(key))

            record = Record(by=models.User.objects.get(id=request.session['id']),
                            to=quiz,
                            points=check_user_quiz(answers, current_id),
                            date=datetime.datetime.now())
            record.save()
            return home(request, "You scored " + str(record.points) + " in " + str(quiz.name) + " quiz!")
        else:
            return render(request, 'quiz/run.html', {'quiz': quiz, 'tasks': tasks})


def check_user_quiz(answers, quiz_id):
    """
    Calculation of user quiz result
    :param answers: list of checked Answers
    :param quiz_id: id of Quiz
    :return: Amount of points
    """
    result = models.Quiz.objects.get(id=quiz_id).points
    max_amount_of_points = 0
    for i in models.Question.objects.filter(to=quiz_id):
        max_amount_of_points += i.points
        user_correct = user_answers = question_correct = 0
        for j in models.Answer.objects.filter(to=i.id):
            # User answers
            if int(j.id) in answers:
                if j.correct:
                    user_correct += 1
                user_answers += 1
            # Right answers
            if j.correct:
                question_correct += 1

        # ZERO DIVISION FIX
        if user_answers == 0:
            result += 0
        elif question_correct == 0:
            result += i.points
        else:
            result += float(i.points * user_correct) / (question_correct * user_answers)
    result -= max_amount_of_points
    return result


def login(request):
    """
    Logging user
    :param request: HTTP request
    :return:
    """
    if request.method == "POST":
        login_form = forms.LoginForm(request.POST)
        error = None
        try:
            login_form.is_valid()
            current = User.objects.get(email=login_form.cleaned_data['email'])
            if not current.check_password(login_form.cleaned_data['password']):
                error = "Wrong password."
        except ObjectDoesNotExist:
            error = "No such user."
        except KeyError:
            error = "Nice try. Input valid data plz."
        if error is not None:
            return render(request, 'quiz/login.html', {'error': error, 'form': login_form})
        else:
            request = start_user_session(request, current)
            return home(request, "Welcome back!")
    else:
        login_form = forms.LoginForm()
        return render(request, 'quiz/login.html', {'form': login_form})


def logout(request):
    """
    Logging out user
    :param request: HTTP request
    :return:
    """
    request = end_user_session(request)
    return login(request)


def signup(request):
    """
    Register user
    :param request: HTTP request
    :return:
    """
    if request.method == "POST":
        sign_up_form = forms.SignUpForm(request.POST)
        sign_up_form.is_valid()
        try:
            u = User(email=sign_up_form.cleaned_data['email'], username=sign_up_form.cleaned_data['username'])
            error = u.check_existence()

            if sign_up_form.cleaned_data['password'] != sign_up_form.cleaned_data['password_repeat']:
                error = "Passwords didn't match."
        except KeyError:
            error = "Mistakes!"
        if error is None:
            u.set_password(sign_up_form.cleaned_data['password'])
            u.save()
            return home(request, message='Successful!')
        else:
            return render(request, 'quiz/signup.html', {'error': error, 'form': sign_up_form})
    else:
        sign_up_form = forms.SignUpForm()
        return render(request, 'quiz/signup.html', {'form': sign_up_form})


def profile(request, user_id=None):
    if user_id is None:
        user = models.User.objects.get(id=request.session['id'])
        info_form = ProfileEditForm(initial={'email': user.email,
                                             'username': user.username,
                                             'first_name': user.first_name,
                                             'last_name': user.last_name,
                                             'image': user.image})
        password_form = ProfilePasswordEditForm()
        return render(request, 'quiz/profile.html', {'info_form': info_form,
                                                     'password_form': password_form})
    else:
        records = models.Record.objects.filter(by=user_id).order_by('-date')
        return render(request, 'quiz/profile.html', {'user': models.User.objects.get(id=user_id),
                                                     'records': records})


def password_change(request):
    """
    Changing personal info of current user
    :param request: HTTP POST request
    :return:
    """
    if request.method == 'POST' and check_user_session(request):
        form = ProfilePasswordEditForm(request.POST)
        form.is_valid()
        user = User.objects.get(id=request.session['id'])
        if user.check_password(form.cleaned_data['old_password']) and form.cleaned_data['password_repeat'] == \
                form.cleaned_data['password']:
            user.set_password(form.cleaned_data['password'])
            user.save()
            end_user_session(request)
            return home(request, "Success! You changed password! Try to use it.")
        else:
            return home(request, "You messed up something.")

    else:
        return home(request, "Ops! Something went wrong. :(")


def info_change(request):
    """
    Changing info from form
    :param request: HTTP request POST
    :return:
    """
    if request.method == 'POST' and check_user_session(request):
        form = ProfileEditForm(request.POST, request.FILES)
        form.is_valid()

        user = User.objects.get(id=request.session['id'])
        user.email = form.cleaned_data['email']
        user.username = form.cleaned_data['username']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        if form.cleaned_data['image']:
            user.image = form.cleaned_data['image']
        user.save()
        return home(request, "Everything was changed. Check it out!")
    else:
        return home(request, "Ops! Something went wrong. :(")


def quiz_board(request):
    """
    Table of all quizes
    :param request: HTTP request
    :return:
    """
    if check_user_session(request):
        return render(request, 'quiz/quiz_board.html', {'quizes': Quiz.objects.all().order_by('-date')})
    else:
        return home(request, "You first step is registration friend ;)")
        # TODO Refactor


def records(request):
    """
    Table of records
    :param request:
    :return:
    """
    all_records = models.Record.objects.all().order_by('-date')
    return render(request, 'quiz/records.html', {'records': all_records})
