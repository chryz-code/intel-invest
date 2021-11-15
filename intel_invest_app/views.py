from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import smtplib
import ssl

# Create your views here.
def loginPage(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
             
    return render(request,'registration/login.html', context)

def registerPage(request):
    form = SignupForm
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect ('home')
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'registration/register.html', {'form':form})

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'home.html')

@login_required(login_url='login')
def addPackage(request):
    if request.user.is_superuser:
        form = PackagesForm
        if request.method == 'POST':
            form = PackagesForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect ('all-packages')
        return render(request, 'packages.html', {'form':form})
    else:
        return redirect('home')

@login_required(login_url='login')
def editPackage(request, package_id):
    if request.user.is_superuser:
        package = Packages.objects.get(pk=package_id)
        form = PackagesForm(instance=package)
        if request.method == 'POST':
            form = PackagesForm(request.POST, instance=package)
            if form.is_valid():
                form.save()
                return redirect ('all-packages')
        return render(request, 'packages.html', {'form':form})
    else:
        return redirect('home')

@login_required(login_url='login')
def allPackages(request):
    if request.user.is_superuser:
        packages = Packages.objects.all()
        context = {'packages':packages}
        return render(request, 'all-packages.html', context)
    else:
        return redirect('home')

@login_required(login_url='login')
def deletePackage(request, pk):
    if request.user.is_superuser:
        package = Packages.objects.get(pk=pk)
        package.delete()
        return redirect('all-packages')
    else:
        return redirect('home')

@login_required(login_url='login')
def pacakageDetail(request, package_id):
        user = request.user
        package = Packages.objects.get(pk=package_id)
        context = {'package':package, 'user':user}
        return render(request, 'package-detail.html', context)

def faqspage(request):
    return render(request, 'faq-pages.html')

def aboutus(request):
    return render(request, 'about-us.html')

def rules(request):
    return render(request, 'rules.html')

@login_required(login_url='login')
def userProfile(request, username):
    user = get_object_or_404(User, username=username)
    package_invested = Packages.objects.filter(investors=user)
    wallets = UserWallet.objects.filter(user=user)[:1]
    total_investment_price = 0
    for package in package_invested:
        total_investment_price += package.package_price

    if request.user == user.is_superuser or request.user :
        context = {'user':user, 'package_invested':package_invested, 'total_investment_price':total_investment_price}
        return render(request, 'user-profile.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
def payment(request):
    port = settings.EMAIL_PORT
    smtp_server = settings.EMAIL_HOST
    receiver_email = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    sender_email = request.user.email
    form = PaymentForm
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            subject = "Investment Payment"
            body = {
                'cryptocurrency': request.POST['cryptocurrency'],
                'transanction_hash': request.POST['transanction_hash'],
                'package': request.POST['package'],
            }
            message = "\n".join(body.values())
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return redirect ('user-profile', request.user.username)
    context = {'form':form}
    return render(request, 'payment.html', context)

@login_required(login_url='login')
def addUserWallet(request):
    form = UserWalletForm
    wallets = UserWallet.objects.filter(user=request.user)
    if wallets:
        return redirect('user-profile', request.user.username)
    
    if request.method == 'POST':
        form = UserWalletForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user                                                
            form.save()
            return redirect ('user-profile', request.user.username)

    return render(request, 'add-user-wallets.html', {'form':form})


