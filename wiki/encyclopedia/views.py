from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from markdown2 import Markdown
import random

from . import util


class EntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 15px;'}), label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'margin-bottom: 15px;'}), label="Enter Markdown Content")



def markdown_to_html(title):
    '''
    Coverts markdown content to html
    '''

    content = util.get_entry(title)

    if content is None:
        print("Not found!")
        return None

    print("Found!")
    return mark_safe(Markdown().convert(content))


def entry(request, title):
    '''
    Render encyclopedia entry content based on title.
    '''

    content = markdown_to_html(title)

    if content is None:
        return render(request, 'encyclopedia/error.html', {
            'error_message' : f"Requested page '{title}' was not found!!! 🙁"
        })
    
    return render(request, 'encyclopedia/entry.html', {
        'content' : content,
        'title' : title
    })


def search(request):
    '''
    Match search result to query. 
    '''
    if request.method == "POST":
        title = request.POST.get('q')  
        content = markdown_to_html(title)
        
        # If the query matches the name of an encyclopedia entry redirect to entry.
        if content is not None:
            return HttpResponseRedirect(reverse('entry', args=[title]))
    
        # Show results of substrings.
        entries = util.list_entries()
        sub_entries = []
        for entry in entries:
            if title.lower() in entry.lower():
                sub_entries.append(entry)
        return render(request, "encyclopedia/index.html", {
            "entries": sub_entries
        })  
    
    return HttpResponseRedirect(reverse('index'))


def new_page(request):
    '''
    Create new encyclopedia entry.
    '''
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']

        # If entry exists display error
        for entry in util.list_entries():
            if title.lower() in entry.lower():
                return render(request, "encyclopedia/error.html", {
            'error_message' : f"Sorry, a page '{title}' already exits... 🙁"
        })

        # Save new entry to disk and display. 
        util.save_entry(title, content)
        markdown_to_html(title)
        return HttpResponseRedirect(reverse('entry', args=[title]))
    
    # Display form for creation of markdown content.
    return render(request, "encyclopedia/new_page.html", {
        "form": EntryForm()
    })


def random_page(request):
    entries = util.list_entries()

    # Choose random entry and redirect
    random_entry = random.choice(entries)
    return HttpResponseRedirect(reverse('entry', args=[random_entry]))

def save(request):
    '''
    Saves changes made to edits.
    '''
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        util.save_entry(title, content)
        markdown_to_html(title)
        return HttpResponseRedirect(reverse('entry', args=[title]))

    return HttpResponseRedirect(reverse('index'))


def edit(request):
    '''
    Edit existing encyclopedia entry.
    '''
    if request.method == 'POST':
        title = request.POST['title']
        content = util.get_entry(title)
        form = EntryForm(initial={'title': title, 'content': content})
        return render(request, "encyclopedia/edit.html", {
            "form": form
        })
    
    return HttpResponseRedirect(reverse('index'))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

