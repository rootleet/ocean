from django.shortcuts import render, HttpResponse, redirect
from blog.forms import *
from blog.anton import *
from blog.models import *

# general values
search_form = SearchForm()


# Create your views here.
def index(request):
    artcs = articles.objects.all()[:10]
    context = {
        'page_title': 'Ocean | The Power In Sharing',
        'search_form': search_form,
        'artcs': artcs
    }
    return render(request, 'blog/index.html', context)


def article(request, title):
    this_article = articles.objects.get(title=title)
    context = {
        'page_title': 'Ocean | Article | ' + str(title),
        'search_form': search_form,
        'article': this_article
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
    context = {
        'page_title': 'Ocean | Search | ' + str(query[0:20])
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
