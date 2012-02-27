from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from quiz.models import QuizProfile, Question, AttemptedQuestion
from django.contrib.auth.decorators import login_required
import random, string, hashlib,datetime
from django.template import RequestContext
from quiz.forms import QuestionForm
from static_pages.models import Page
import hashlib
from django.contrib.sites.models import Site
from quiz.create_excel import ExcelResponse

def calc_time(a, b):
    td = b - a
    seconds = td.days*24*3600 + td.seconds + td.microseconds/10**6
    return seconds

def share_rank(request, fb_share_key):
    context = RequestContext(request)
    qp_set = QuizProfile.objects.all().order_by('-total_score')
    players_count = len(qp_set)
    if len(qp_set)>10:
        top_ten = qp_set[:10]
    else:
        top_ten = qp_set
    rank = 1
    for qp in qp_set:
        qp.fb_share_key
        if qp.fb_share_key == fb_share_key:
            qp.fb_share_key = ''.join(random.choice(string.letters) for i in xrange(300))
            qp.save()
            return render_to_response( "quiz/facebook_share.html", {"quiz_profile":qp, "rank":rank,"top_ten":top_ten, "players_count":players_count, }, context_instance = context)
        rank += 1
    return HttpResponseRedirect("/quiz/")

def quiz_not_active(request):
    context = RequestContext(request)
    return render_to_response( "quiz/quiz_not_active.html", {}, context_instance = context)

def index(request):
    context = RequestContext(request)
    return render_to_response( "quiz/index.html", {}, context_instance = context)

@login_required
def dashboard(request):
    context = RequestContext(request)
    quiz = Page.objects.get(slug="online-quiz")
    site = Site.objects.all()[0]
    if not QuizProfile.objects.all().filter(user=request.user):
        quiz_profile = QuizProfile(user=request.user, total_score = 0.0, fb_share_key = ''.join(random.choice(string.letters) for i in xrange(300)))
        quiz_profile.save()
    else:
        quiz_profile = get_object_or_404(QuizProfile, user=request.user)
    qp_set = QuizProfile.objects.all().order_by('-total_score')
    players_count = len(qp_set)
    
    if request.user.is_superuser:
        top_hundread = qp_set
    else:
        if len(qp_set)>100:
            top_hundread = qp_set[:100]
        else:
            top_hundread = qp_set
    
    rank = 1
    for qp in qp_set:
        if qp == quiz_profile:
            break
        rank += 1
    
    return render_to_response( "quiz/dashboard.html", {"quiz_profile":quiz_profile,"rank":rank, "top_hundread":top_hundread,"site":site, "players_count":players_count, "quiz":quiz,}, context_instance = context)


@login_required
def show_new_question(request):
    context = RequestContext(request)
    if not QuizProfile.objects.all().filter(user=request.user):
        quiz_profile = QuizProfile(user=request.user, total_score = 0.0, fb_share_key = ''.join(random.choice(string.letters) for i in xrange(300)))
        quiz_profile.save()
    else:
        quiz_profile = get_object_or_404(QuizProfile, user=request.user)
    if request.method == 'POST': # If the form has been submitted...
        form = QuestionForm(request.POST)
        if form.is_valid():
            submitted_option = form.cleaned_data['correct_option']
            submitted_question = get_object_or_404(Question, pk= int(request.POST['question']))
            attempted_question = get_object_or_404(AttemptedQuestion, player = quiz_profile, question = submitted_question,)

            if attempted_question.answered:
                return HttpResponseRedirect("/quiz/")

            time_taken = float(request.POST['time_taken'])

            marks = 0.0
            if submitted_question.correct_option == int(submitted_option):
                success = True
                if time_taken <= submitted_question.max_time and time_taken >= submitted_question.min_time:
                    marks = submitted_question.max_marks*submitted_question.min_time/time_taken
                elif time_taken < submitted_question.min_time:
                    marks = submitted_question.max_marks
            else:
                success = False
            marks = round(marks,2)

            alert = False
            attempted_question.time_taken = time_taken
            attempted_question.server_time_taken = calc_time(attempted_question.time, datetime.datetime.now())

            if attempted_question.server_time_taken - attempted_question.time_taken > 10:
                marks = 0.0
                alert = True


            attempted_question.marks_obtained = marks
            attempted_question.answered = True
            attempted_question.save()
            
            quiz_profile.update()
            return render_to_response( "quiz/submit_done.html", {"opt":submitted_option, "success":success,"question": submitted_question, "marks":marks, "time":time_taken, "alert":alert, }, context_instance = context)
    else:
        form = QuestionForm()
        questions = Question.objects.all()
        attempted_questions = AttemptedQuestion.objects.all().filter(player__user = request.user)

        limit_exceeded = False
        aqs_today = AttemptedQuestion.objects.filter(player__user= request.user, time__day=datetime.datetime.now().day)
        aqs = []
        daily_limit = 30
        
        if len(questions) == len(attempted_questions) or len(questions) == 0 or aqs_today.count() >= daily_limit :
            if aqs_today.count() >= daily_limit:
                limit_exceeded = True
            return render_to_response( "quiz/no_active_question.html",{"limit_exceeded":limit_exceeded, "daily_limit":daily_limit}, context_instance = context)
            
        for a in attempted_questions:
            try:
                aqs.append(a.question)
            except:
                continue
        
        while True:            
            q = questions[random.randint(0, len(questions)-1)]
            if q in aqs:
                continue
            else:
                break

        attempted_question = AttemptedQuestion(question = q, player = quiz_profile)
        attempted_question.save()

        quiz_profile.update()
        return render_to_response( "quiz/show_new_question.html", {"question":q, "form":form }, context_instance = context)

@login_required
def show_answers(request):
    context = RequestContext(request)
    q_set = Question.objects.all()
    data_list = [
        ["Question", "Option 1", "Option 2", "Option 3", "Option 4", "Correct Answer", "Maximum Marks", "Soft Time Limit", "Hard Time Limit"],
        ]

    for q in q_set:
            data_list.append(
                [q.title, q.option1, q.option2, q.option3, q.option4, q.correct_option, q.max_marks, q.min_time, q.max_time]
                )       

    return ExcelResponse(data_list, output_name='Prakriti\'11 Online Quiz - Answers')

@login_required
def show_player_attempts(request):
    context = RequestContext(request)
    aqs_set = AttemptedQuestion.objects.all().filter(player__user = request.user).order_by('time')
    data_list = [
        ["Date/Time", "Question", "Option 1", "Option 2", "Option 3", "Option 4", "Correct Answer", "Maximum Marks", "Obtained Marks", "Soft Time Limit", "Hard Time Limit", "Time Taken", "Time Recorded by Server Side Timer"],
        ]

    for a in aqs_set:
            data_list.append(
                [a.time, a.question.title, a.question.option1, a.question.option2, a.question.option3, a.question.option4, a.question.correct_option, a.question.max_marks, a.marks_obtained, a.question.min_time, a.question.max_time, a.time_taken, a.server_time_taken]
                )       

    return ExcelResponse(data_list, output_name='Prakriti\'11 Online Quiz - Attempts by ' + str(request.user.username))


