import datetime
import hashlib
from static.general.anton import *
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from community.models import *


# VIEW :: Home of community
def index(request):
    quests = questions.objects.all()
    context = {
        'page_title': 'Community',
        'quests': quests
    }
    return render(request, 'community/index.html', context=context)


# VIEW :: View a question in details
def view_question(request, question_id):
    current_user = request.user
    user_id = current_user.id
    question = questions.objects.filter(title=question_id)
    # counted_views = question.get().views + 1
    # questions.objects.filter(title=question_id).update(views=counted_views)

    quest = question.get()
    comments = answers.objects.filter(question=quest.uni)

    context = {
        'page_title': question_id,
        'question': quest,
        'comments_count': comments.count(),
        'comments': comments
    }
    # insert into view
    if QuestionViews.objects.filter(question=quest.uni).count() < 1:
        QuestionViews(question=quest.uni, user=user_id).save()
    return render(request, 'community/question.html', context=context)


# VIEW :: Asking Question
def ask_question(request):
    if request.user.is_active == False:
        return redirect('login')
    communities = tags.objects.all()
    context = {
        'page_title': 'Ocean | Community | Question Title',
        'communities': communities
    }
    return render(request, 'community/new-question.html', context=context)


# FUNC :: Submit a new question
def submit_question(request):  # submitting a question
    current_user = request.user
    user_id = current_user.id

    if request.method == "POST":
        form = request.POST
        title = form['title']
        body = form['body']
        community = form.getlist('community')

        md_mix = str(title) + str(body) + str(community) + str(current_user.id)
        hash_object = hashlib.md5(md_mix.encode())
        md5_hash = hash_object.hexdigest()

        # save into questions
        commit_question = questions(uni=md5_hash, title=title, body=body, owner=user_id)
        try:
            commit_question.save()
            for x in community:
                QuestionTags(question=commit_question.uni, tag=x).save()

            messages.success(request, "Question Asked Successfully")
            return redirect('view_question', title)
            # return HttpResponse(f'done%%Process Completed Successfully')


        except:
            messages.success(request, "Question was not submitted successfully")
            return redirect('questions')
            return HttpResponse(f'error%%Question Could Not Be Submitted')

    else:
        return HttpResponse('error%%invalid_forms')


def new_comment(request):
    current_user = request.user
    user_id = current_user.id
    if request.method == "POST":
        form = request.POST
        ans = form['body']
        ques = form['ques']

        try:
            answers(question=ques, ans=ans, user=user_id).save()
            return HttpResponse('done%%Answer Issues Successfully')
        except:
            return HttpResponse(f'error%%Issues Submitting Answer')
