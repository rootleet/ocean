from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(max_length=200)


class NewArticle(forms.Form):
    page_title = forms.CharField(max_length=200)
    article_desc = forms.CharField(max_length=5000)
    meta = forms.CharField(max_length=100)
    post_img = forms.ImageField()


class EdArticle(forms.Form):
    page_title = forms.CharField(max_length=200)
    article_desc = forms.CharField(max_length=5000)
    meta = forms.CharField(max_length=100)
    uni = forms.CharField(max_length=100)




class LogIn(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(max_length=200)
