from django.shortcuts import render ,redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import Feedback ,Enrollment
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import requests
import json

def index(request):
    user=User.objects.all()
    context={
        user: user,
    }
    return render(request, 'form/index.html',context)

def login_view(request): 
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('pass')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            return redirect('index')
        else:
            
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'form/login.html')

def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('pass')
        phone=request.POST.get('phone')
        password_confirm = request.POST.get('pass2')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'form/singin.html', {'error': 'Username already exists'})
        
        if password == password_confirm:
            try:
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.save()
                
                
                subject = 'Account Creation Confirmation'
                message = f'Hello {username},\n\n account has been successfully created.\n\n phone no :: {phone}'
                from_email = settings.EMAIL_HOST_USER
                to_email = [email,'atul.saini.techstack@gmail.com']
                send_mail(subject, message, from_email, to_email)
                
                return render(request, 'form/singin.html', {'success': 'Account created successfully. Please check your email for confirmation.'})
            except IntegrityError:
                return render(request, 'form/singin.html', {'error': 'Failed to create user'})
        else:
            return render(request, 'form/singin.html', {'error': 'Passwords do not match'})
    return render(request, 'form/singin.html')
def logout_view(request):
    logout(request)
    return redirect('index') 

def connect_view(request):
    if request.method == 'POST':
        name = request.POST.get('uname', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        msg = request.POST.get('msg', '')

        try:
            # Save form data
            fomet = Feedback(name=name, email=email, phone=phone, msg=msg)
            fomet.save()

            # Send email
            subject = 'New Feedback from {}'.format(name)
            message = 'Name: {}\nEmail: {}\nPhone: {}\nMessage: {}'.format(name, email, phone, msg)
            from_email = settings.EMAIL_HOST_USER
            to_email = ['atul.saini.techstack@gmail.com',
                        ]  
            send_mail(subject, message, from_email, to_email)

            
            enrollment_success = "Enrollment successful!"
            email_success = "Email sent successfully!"
            return render(request, 'form/form.html', {'enrollment_success': enrollment_success, 'email_success': email_success})
        except Exception as e:
            
            enrollment_error = "An error occurred while saving the data to the database."
            email_error = f"An error occurred while sending the email: {str(e)}"
            return render(request, 'form/form.html', {'enrollment_error': enrollment_error, 'email_error': email_error})
    
    return render(request, 'form/form.html')




razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))



@login_required
def webdev(request):
    currency = 'INR'
    amount =  100 # Rs. 200
 
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request,"form/reg1.html",context)


@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 100  # Rs. 899
                try:
 
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:
 
                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:
 
                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()






@login_required
def python(request):
    enrollment_error = None
    email_error = None
    enrollment_success = None
    email_success = None

    if request.method == 'POST':
        username = request.POST.get('username', '')
        payment_date = request.POST.get('payment_date', '')
        transaction_id = request.POST.get('transaction_id', '')
        whatsapp_no = request.POST.get('whatsapp_no', '')

        
        try:
            enrollment = Enrollment.objects.create(
                username=username,
                payment_date=payment_date,
                transaction_id=transaction_id,
                whatsapp_no=whatsapp_no
            )
            enrollment.save()
            enrollment_success = "Enrollment successful!"
        except Exception as e:
            enrollment_error = "An error occurred while saving the data to the database."

        
        subject = 'New python Course Enrollment'
        message = f'Username: {username}\nPayment Date: {payment_date}\nTransaction ID: {transaction_id}\nWhatsApp No: {whatsapp_no}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['atul.saini.techstack@gmail.com']

        try:
            send_mail(subject, message, from_email, recipient_list)
            email_success = "Email sent successfully!"
        except Exception as e:
            email_error = f"An error occurred while sending the email: {str(e)}"

    return render(request, 'form/reg2.html', {'enrollment_error': enrollment_error, 'email_error': email_error, 'enrollment_success': enrollment_success, 'email_success': email_success})

@login_required
def datasci(request):
    enrollment_error = None
    email_error = None
    enrollment_success = None
    email_success = None

    if request.method == 'POST':
        username = request.POST.get('username', '')
        payment_date = request.POST.get('payment_date', '')
        transaction_id = request.POST.get('transaction_id', '')
        whatsapp_no = request.POST.get('whatsapp_no', '')

        
        try:
            enrollment = Enrollment.objects.create(
                username=username,
                payment_date=payment_date,
                transaction_id=transaction_id,
                whatsapp_no=whatsapp_no
            )
            enrollment.save()
            enrollment_success = "Enrollment successful!"
        except Exception as e:
            enrollment_error = "An error occurred while saving the data to the database."

        
        subject = 'New datasic Course Enrollment'
        message = f'Username: {username}\nPayment Date: {payment_date}\nTransaction ID: {transaction_id}\nWhatsApp No: {whatsapp_no}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['atul.saini.techstack@gmail.com']
        
        try:
            send_mail(subject, message, from_email, recipient_list)
            email_success = "Email sent successfully!"
        except Exception as e:
            email_error = f"An error occurred while sending the email: {str(e)}"

    return render(request, 'form/reg3.html', {'enrollment_error': enrollment_error, 'email_error': email_error, 'enrollment_success': enrollment_success, 'email_success': email_success})

@login_required
def machine(request):
    enrollment_error = None
    email_error = None
    enrollment_success = None
    email_success = None

    if request.method == 'POST':
        username = request.POST.get('username', '')
        payment_date = request.POST.get('payment_date', '')
        transaction_id = request.POST.get('transaction_id', '')
        whatsapp_no = request.POST.get('whatsapp_no', '')

        
        try:
            enrollment = Enrollment.objects.create(
                username=username,
                payment_date=payment_date,
                transaction_id=transaction_id,
                whatsapp_no=whatsapp_no
            )
            enrollment.save()
            enrollment_success = "Enrollment successful!"
        except Exception as e:
            enrollment_error = "An error occurred while saving the data to the database."

        
        subject = 'New ML Course Enrollment'
        message = f'Username: {username}\nPayment Date: {payment_date}\nTransaction ID: {transaction_id}\nWhatsApp No: {whatsapp_no}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['atul.saini.techstack@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
            email_success = "Email sent successfully!"
        except Exception as e:
            email_error = f"An error occurred while sending the email: {str(e)}"

    return render(request, 'form/reg4.html', {'enrollment_error': enrollment_error, 'email_error': email_error, 'enrollment_success': enrollment_success, 'email_success': email_success})

@login_required
def datatc(request):
    enrollment_error = None
    email_error = None
    enrollment_success = None
    email_success = None

    if request.method == 'POST':
        username = request.POST.get('username', '')
        payment_date = request.POST.get('payment_date', '')
        transaction_id = request.POST.get('transaction_id', '')
        whatsapp_no = request.POST.get('whatsapp_no', '')

        
        try:
            enrollment = Enrollment.objects.create(
                username=username,
                payment_date=payment_date,
                transaction_id=transaction_id,
                whatsapp_no=whatsapp_no
            )
            enrollment.save()
            enrollment_success = "Enrollment successful!"
        except Exception as e:
            enrollment_error = "An error occurred while saving the data to the database."

        
        subject = 'New data anilist Course Enrollment'
        message = f'Username: {username}\nPayment Date: {payment_date}\nTransaction ID: {transaction_id}\nWhatsApp No: {whatsapp_no}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['atul.saini.techstack@gmail.com']

        try:
            send_mail(subject, message, from_email, recipient_list)
            email_success = "Email sent successfully!"
        except Exception as e:
            email_error = f"An error occurred while sending the email: {str(e)}"

    return render(request, 'form/reg5.html', {'enrollment_error': enrollment_error, 'email_error': email_error, 'enrollment_success': enrollment_success, 'email_success': email_success})
@login_required
def sql(request):
    enrollment_error = None
    email_error = None
    enrollment_success = None
    email_success = None

    if request.method == 'POST':
        username = request.POST.get('username', '')
        payment_date = request.POST.get('payment_date', '')
        transaction_id = request.POST.get('transaction_id', '')
        whatsapp_no = request.POST.get('whatsapp_no', '')

        # Save data to the database
        try:
            enrollment = Enrollment.objects.create(
                username=username,
                payment_date=payment_date,
                transaction_id=transaction_id,
                whatsapp_no=whatsapp_no
            )
            enrollment.save()
            enrollment_success = "Enrollment successful!"
        except Exception as e:
            enrollment_error = "An error occurred while saving the data to the database."

        # Send email
        subject = 'New sql Course Enrollment'
        message = f'Username: {username}\nPayment Date: {payment_date}\nTransaction ID: {transaction_id}\nWhatsApp No: {whatsapp_no}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['atul.saini.techstack@gmail.com']

        try:
            send_mail(subject, message, from_email, recipient_list)
            email_success = "Email sent successfully!"
        except Exception as e:
            email_error = f"An error occurred while sending the email: {str(e)}"
            
    return render(request, 'form/reg6.html', {'enrollment_error': enrollment_error, 'email_error': email_error, 'enrollment_success': enrollment_success, 'email_success': email_success})


def index1(request):
    return render(request, 'form\index1.html')


def execute_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        language = request.POST.get('language')

        # Replace these with your own Client ID and Client Secret
        CLIENT_ID = "beee2674d3eed2d221514e6e3b4592f7"
        CLIENT_SECRET = "24cb2d8dd0d5eb2cc3f4d8c8434230b41615bcb3e1ac38a9b554c6ca69c3329e"

        auth_data = {
            'clientId': CLIENT_ID,
            'clientSecret': CLIENT_SECRET
        }
        auth_response = requests.post("https://api.jdoodle.com/v1/auth-token", json=auth_data)
        token = auth_response.json().get('token')

        execution_data = {
            "script": code,
            "language": language,
            "versionIndex": "0",
            "token": token
        }
        execution_response = requests.post("https://api.jdoodle.com/v1/execute", json=execution_data)
        
        print(execution_response.text)  # Add this line to print the response content

        response = json.loads(execution_response.text)
        output = response.get('output')
        error = response.get('error')

        return render(request, 'form/index1.html', {'output': output, 'error': error})
