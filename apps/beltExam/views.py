from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Product, Wishlist

def index(request):
    return render(request, 'beltExam/index.html')

def register(request):
    postData = {
        'first_name': request.POST['first_name'],
        'last_name': request.POST['last_name'],
        'email': request.POST['email'],
        'password': request.POST['password'],
        'confirm': request.POST['confirm'],
        'date': request.POST['date'],
    }
    errors = User.objects.register(postData)
    if len(errors) == 0:
        request.session['id'] = User.objects.get(email=postData['email']).id
        request.session['name'] = postData['first_name']
        return redirect('/dashboard')
    for error in errors:
        messages.info(request, error)
    return redirect('/')

def login(request):
    postData = {
        'email': request.POST['email'],
        'password': request.POST['password']
    }
    errors = User.objects.login(postData)
    if len(errors) == 0:
        request.session['id'] = User.objects.get(email=postData['email']).id
        request.session['name'] = User.objects.get(email=postData['email']).first_name
        return redirect('/dashboard')
    for error in errors:
        messages.info(request, error)
    return redirect('/')

def dashboard(request):
    context = {
        'my_wishes': Wishlist.objects.filter(user_id=request.session['id']).order_by('-created_at'),
        'products': Product.objects.exclude(wishes__user_id=request.session['id']).order_by('-created_at'),
    }
    return render(request, 'beltExam/dashboard.html', context)

def delete(request, id):
    Product.objects.get(id=id).delete()
    return redirect('/dashboard')

def create(request):
    return render(request, 'beltExam/add.html')

def update(request):
    postData = {
        'item': request.POST['product'],
        'userID': request.session['id'],
    }
    errors = Product.objects.check_product(postData)
    if len(errors) == 0:
        return redirect('/dashboard')
    messages.info(request, errors[0])
    return redirect('/create')

def remove(request, uID, pID):
    Wishlist.objects.get(user_id=uID, product_id=pID).delete()
    return redirect('/dashboard')

def add(request, id):
    Wishlist.objects.create(user_id=request.session['id'], product_id=id)
    return redirect('/dashboard')

def show(request, id):
    context = {
        'product': Product.objects.get(id=id),
        'users': User.objects.filter(wishes__product_id=id),
    }
    return render(request, 'beltExam/show.html', context)
