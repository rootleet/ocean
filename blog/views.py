from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests

import blog.urls
from django.contrib.messages.storage import session
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from blog.forms import *
from blog.anton import *
from blog.models import *

# general values
search_form = SearchForm()
all_meta = article_meta.objects.all()


# Create your views here.
def index(request):
    artcs = articles.objects.all().order_by('-id')[:10]
    groups = article_meta.objects.all()

    context = {
        'page_title': 'Ocean | The Power In Sharing',
        'search_form': search_form,
        'artcs': artcs,
        'groups': groups,
        'meta': article_meta.objects.all(),
    }
    return render(request, 'blog/index.html', context)


def article(request, title):
    if 'login' not in request.session:
        logedin = False
        username = False
        meta_kword = False
    else:
        logedin = request.session['login']
        username = request.session['user']
        user_details = userAccounts.objects.get(username=username)
        meta_kword = user_details.meta_words

    this_article = articles.objects.get(title=title)
    context = {
        'page_title': 'Ocean | Article | ' + str(title),
        'search_form': search_form,
        'article': this_article,
        'login': {
            'status': logedin, 'myname': username, 'mymeta': meta_kword
        }
    }
    return render(request, 'blog/article.html', context)


def search(request):
    if request.method == 'POST':

        s_form = SearchForm(request.POST)
        if s_form.is_valid():
            query = s_form.cleaned_data['query']
            return redirect('search-result', query)
            # return HttpResponse("<h1>"+str(query)+"</h1>")
        else:
            return HttpResponse("<h1>Form Not Valid..</h1>")

    else:
        return HttpResponse("<h1>Method is not posting..</h1>")
    # return render(request, 'blog/search-result.html')


def search_result(request, query):
    # get user keywords
    if 'login' not in request.session:
        logedin = False
        username = False
        meta_kword = False
        query_res = articles.objects.filter(meta='public')
        # return redirect('blog-home')
    else:
        logedin = request.session['login']
        username = request.session['user']

        user_details = userAccounts.objects.get(username=username)
        meta_kword = user_details.meta_words
        if meta_kword == '*':
            query_res = articles.objects.filter(intro__regex=query)
        else:
            query_res = articles.objects.filter(meta__contains=meta_kword, intro__regex=query)

    res_count = query_res.count()

    context = {
        'page_title': ' Ocean | Found | ' + str(query[0:20]),
        'result': query_res, 'result_count': res_count, 'query_str': query,
        'login': {
            'status': logedin, 'myname': username, 'mymeta': meta_kword
        }
    }
    return render(request, 'blog/search-result.html', context=context)


def new_article(request):
    form = NewArticle()
    meta_data = article_meta.objects.all()
    context = {
        'page_title': 'Ocean | The Power In Sharing | New Article',
        'form': form,
        'meta_dat': meta_data
    }
    return render(request, 'blog/new-article.html', context=context)


def save_article(request):
    # validate for
    if request.method == 'POST':
        form = NewArticle(request.POST, request.FILES)
        if form.is_valid():
            # get form details
            page_title = form.cleaned_data['page_title']
            article_desc_raw_htm = form.cleaned_data['article_desc']

            article_into = remove_tags(article_desc_raw_htm[0:200])
            uni = make_md5(page_title + str(article_desc_raw_htm))
            owner = 'anton'
            post_img = form.cleaned_data['post_img']
            meta = form.cleaned_data['meta']

            if articles.objects.filter(uni=uni):
                return HttpResponse("article exist")
            else:
                article_save = articles(uni=uni, title=page_title, article=article_desc_raw_htm, intro=article_into,
                                        owner=owner
                                        , image=post_img, meta=meta)

                article_save.save()
                from PIL import Image
                img = Image.open(post_img)  # Open image using self

                if img.height > 300 or img.width > 300:
                    new_img = (622, 350)
                    img.resize(new_img)
                    img.save(post_img)

                return redirect('article', page_title)

            # insert into database


        else:
            return HttpResponse('Form Not Valid')
            # throw error
    else:
        return HttpResponse("Not Posted Form")


def load_meta(request, meta):
    artcs = articles.objects.filter(meta=meta)
    context = {
        'page_title': 'Ocean | Search | ' + str(meta[0:20]),
        'artcs': artcs, 'meta': all_meta
    }
    return render(request, 'blog/meta-load.html', context=context)
    return None


def login(request):
    context = {
        'page_title': 'Ocean | Login',
        'form': LogIn()
    }
    return render(request, 'blog/login.html', context=context)


def login_process(request):
    if request.method == 'POST':
        form = LogIn(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            next = request.POST.get('next', '/')

            # check if user exist
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                # Redirect to a success page.
                return redirect('blog-home')
            else:
                messages.success(request, "There was an error")
                return redirect('login')

        else:
            return HttpResponse("Invalid Form")
    else:
        pass


def logout(request):
    request.session['login'] = False
    return redirect('blog-home')


def edit_article(request, uni):
    form = EdArticle()
    if 'login' not in request.session:
        logedin = False
        username = False
        meta_kword = False
    else:
        logedin = request.session['login']
        username = request.session['user']
        user_details = userAccounts.objects.get(username=username)
        meta_kword = user_details.meta_words

    this_article = articles.objects.get(uni=uni)
    meta_data = article_meta.objects.all()
    context = {
        'page_title': 'Ocean | Article | Edit',
        'search_form': search_form, 'form': form,
        'article': this_article, 'meta_dat': meta_data,
        'login': {
            'status': logedin, 'myname': username, 'mymeta': meta_kword
        }
    }
    return render(request, 'blog/edit_article.html', context)


def edit_save(request):
    # validate for
    if request.method == 'POST':
        form = EdArticle(request.POST, request.FILES)
        if form.is_valid():
            # get form details
            page_title = form.cleaned_data['page_title']
            article_desc_raw_htm = form.cleaned_data['article_desc']
            uni = form.cleaned_data['uni']

            article_into = remove_tags(article_desc_raw_htm[0:200])
            owner = 'anton'
            meta = form.cleaned_data['meta']

            articles.objects.filter(uni=uni).update(title=page_title, intro=article_into, article=article_desc_raw_htm,
                                                    meta=meta)
            return redirect('article', page_title)
            # return HttpResponse('Form Valid')

            # insert into database


        else:
            return HttpResponse('Form Not Valid')
            # throw error
    else:
        return HttpResponse("Not Posted Form")


def finder(request):
    return render(request, 'blog/finder.html')