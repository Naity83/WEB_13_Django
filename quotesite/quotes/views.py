from django.shortcuts import render, redirect
from .utils import get_mongodb
from django.core.paginator import Paginator
from bson.objectid import ObjectId
from .models import Quote, Tag, Author
from .forms import QuoteForm, AuthorForm, TagForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def main(request, page=1):
    db = get_mongodb()
    quotes = db.quotes.find()
    per_page = 10
    paginator = Paginator(list(quotes), per_page)
    quotes_on_page = paginator.page(page)
    print(list(quotes))
    latest_quote = Quote.objects.latest('created_at')
    tags_for_latest_quote = latest_quote.tags.all()
    author_for_latest_quote = Author.objects.get(id=latest_quote.author_id)
    top_tags = Tag.objects.annotate(num_quotes=Count('quote')).order_by('-num_quotes')[:10]
    for i, tag in enumerate(top_tags, start=1):
        tag.css_class = f'tag-{i}'  # Создаем классы вида tag-1, tag-2 и т.д.
    return render(request, 'quotes/index.html', context={'quotes':quotes_on_page, 
                                                         'latest_quote': latest_quote,
                                                          'author_for_latest_quote': author_for_latest_quote, 
                                                          'tags_for_latest_quote': tags_for_latest_quote,
                                                          'top_tags': top_tags,
                                                          })

def author_about(request, author_id):
    db = get_mongodb()
    author = db.authors.find_one({'_id': ObjectId(author_id)})  # Використання ObjectId(author_id)
    return render(request, 'quotes/author.html', context={'author': author})

def tag_page(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    quotes_with_tag = Quote.objects.filter(tags=tag)
    return render(request, 'quotes/tag.html', {'quotes_with_tag': quotes_with_tag, 'tag': tag})


def author_for_tag(request, author_id):
    author = Author.objects.get(id=author_id)
    return render(request, 'quotes/author_for_tag.html', context={'author': author})


@login_required  # Проверяет, что пользователь авторизован, прежде чем позволить доступ к представлению.
def add_author(request):  # Обработчик запроса для добавления нового автора.
    if request.method == 'POST':  # Проверка метода запроса (POST или GET).
        form = AuthorForm(request.POST)  # Создание формы на основе POST данных.
        if form.is_valid():  # Проверка валидности данных из формы.
            new_author = form.save(commit=False)  # Создание нового автора без сохранения в БД.
            new_author.user = request.user  # Установка пользователя как создателя автора.
            new_author.save()  # Сохранение автора в БД.
            return redirect(to='quotes:root')  # Перенаправление на главную страницу.
        else:
            return render(request, 'quotes/add_author.html', context={'form': form})  # Отображение формы с ошибками валидации.
    return render(request, 'quotes/add_author.html', context={'form': AuthorForm()})  # Отображение пустой формы для ввода.


@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            new_quote = form.save(commit=False)
            new_quote.user = request.user
            new_quote.save()
            tag_name = form.cleaned_data["tags"]
            for tag in tag_name:
                new_quote.tags.add(tag.id)
            new_quote.save()
            return redirect(to='quotes:root')
        else:
            return render(request, 'quotes/add_quote.html', context={'form': form})
    return render(request, 'quotes/add_quote.html', context={'form': QuoteForm()})


@login_required
def add_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            return redirect(to='quotes:root')
        else:
            return render(request, 'quotes/add_tag.html', context={'form': form})
    return render(request, 'quotes/add_tag.html', context={'form': TagForm()})








