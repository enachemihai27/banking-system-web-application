import os
import string
from datetime import datetime
import random

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render
from django.contrib.auth.models import User
from twilio.rest import Client

from .models import Profile, Transaction
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import SignUpForm, EditProfileForm, PasswordChangeForm, ProfileForm, SimpleForm, ContractForm, TransactionForm,\
    CodeForm, DateFilterForm,DepositForm, ResetPasswordFrom,TransactionIbanForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from datetime import datetime
UserModel = get_user_model()
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, InvalidPage




def index(request):



    return render(request, 'bank/index.html')


def register(request):
    form = SignUpForm(request.POST or None)
    profile_form = ProfileForm(request.POST or None)
    if form.is_valid() and profile_form.is_valid():

        user = form.save(commit=False)
        profile = profile_form.save(commit=False)
        phone = profile_form.cleaned_data['phone']
        user.is_active = True
        profile.user = user
        if   profile_form.cleaned_data['birth_date'] == None:
            age_error = True
        else:
            age_error = profile_form.clean_date_of_birth()

        number_error = False
        all_users = User.objects.all()
        for usr in all_users:
            if usr.profile.phone == phone:
                number_error = True

        if(age_error or number_error):
            context = None
            if age_error == True and number_error ==False:
                context = {
                    "form": form,
                    "profile_form": profile_form,
                    "error_message": "Trebuie sa ai minim 18 ani!"
                }
            elif age_error == False and number_error ==True:
                context = {
                    "form": form,
                    "profile_form": profile_form,
                    "error_message": "Exista deja un cont asociat numarului de telefon!"
                }
            elif age_error == True and number_error ==True:
                context = {
                    "form": form,
                    "profile_form": profile_form,
                    "error_message": "Trebuie sa ai minim 18 ani si exista deja un cont asociat numarului de telefon!"
                }

            return render(request, 'bank/register.html', context)
        else:

            user.save()
            profile.save()

            group = Group.objects.get(name='Client')
            user.groups.add(group)

            return redirect(acc_created)

    context = {
        "form": form,
        "profile_form":profile_form,
    }
    return render(request, 'bank/register.html', context)


def acc_created(request):
    return render(request, 'bank/acc_created.html')



def login_usr(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        login_code = random.randint(100000, 999999)
        print(login_code)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if user.groups.all()[0].name == 'Client':

                    # VERIFICARE TELEFON
                    # user_phone_number = user.profile.phone
                    # account_sid = 'ACdf410258a2a7facd104413335b7d44f6'
                    # auth_token = 'f6485783cb61ca8860cac9305afda918'
                    # client = Client(account_sid, auth_token)
                    #
                    # message = client.messages \
                    #     .create(
                    #     body=f"Salut {user.first_name}, te-ai conectat la contul tau de Federal Bank.Codul de confirmare este {login_code}",
                    #     from_='+12096650211',
                    #     to=str(user_phone_number)
                    # )
                    #
                    # print(message.sid)


                    request.session['login_details'] = {}
                    upd = {
                        'login_code': login_code,
                        'username' :username,
                        'password': password,
                    }
                    request.session['login_details'].update(upd)
                    return redirect(verify_login)
                else:
                    login(request, user)
                    return redirect(index)

            else:
                return render(request, 'bank/login.html')
        else:
            return render(request, 'bank/login.html', {'error_message': 'Invalid login'})
    return render(request, 'bank/login.html')

def verify_login(request):
    form = CodeForm(request.POST or None)

    if request.method == 'POST':
        form = CodeForm(request.POST or None)
        if form.is_valid():
            code = form.cleaned_data['code']

            if 'login_details' in request.session:
                transaction_details = request.session['login_details']

                if str(code) == str(transaction_details['login_code']):
                    user = authenticate(username=transaction_details['username'], password=transaction_details['password'])
                    login(request, user)

                    return redirect(client_menu)


        else:

            form = CodeForm(request.POST or None)
            context = {'form': form,
                       }

            return render(request, 'bank/verify_login.html', context)

    context = {'form': form,
               }

    return render(request, 'bank/verify_login.html', context)



def logout_usr(request):
    logout(request)

    return redirect(index)


def profile(request):



    context = {'user': request.user,

               }

    return render(request, 'bank/profile.html', context)


def edit_profile(request):
    user = request.user

    form = EditProfileForm(request.POST, instance=user)
    profile_form = ProfileForm(request.POST, instance=user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user)
        if form.is_valid() and profile_form.is_valid():
            form.save()

            usr = form.save(commit=False)

            prf = Profile.objects.filter(user=user)
            current_profile = prf.get()
            phone = profile_form.cleaned_data['phone']
            company_name = profile_form.cleaned_data['company_name']
            address = profile_form.cleaned_data['address']
            current_profile.user = usr
            current_profile.phone = phone
            current_profile.company_name = company_name
            current_profile.address = address

            usr.save()
            profile_form.save()
            current_profile.save()

            return redirect(profile)


    else:
        form = EditProfileForm(instance=user)
        profile_form = ProfileForm(request.POST, instance=user)
        context = {'form': form, 'profile_form':profile_form}

        return render(request, 'bank/edit_profile.html', context)

    context = {'form': form, 'profile_form': profile_form, 'user':user}

    return render(request, 'bank/edit_profile.html', context)




def change_password(request):
    form = PasswordChangeForm(data=request.POST, user=request.user)
    posted = None
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        posted = True

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Parola ta a fost schimbata cu succes!!')
            return redirect(password_changed)
        else:
            context = {'form': form,
                       'posted': posted,

                       }
            return render(request, 'bank/change_password.html', context)

    context = {'form': form,
               'posted': posted,

               }

    return render(request, 'bank/change_password.html', context)


def password_changed(request, ):
    return render(request, 'bank/password_changed.html')

def reset_password(request, user_id):

    user = User.objects.get(id=user_id)
    form = ResetPasswordFrom(request.POST or None)
    password_error = False

    if request.method == 'POST':
        form = ResetPasswordFrom(request.POST or None)


        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']


            if password1 == password2:
                user.set_password(password1)
                user.save()

                return redirect(administrator_menu)
            else:
                password_error = True

                context = {'form': form,
                           'password_error': password_error
                           }
                return render(request, 'bank/reset_password.html', context)

        else:
            context = {'form': form,
                       'password_error': password_error

                       }
            return render(request, 'bank/reset_password.html', context)

    context = {'form': form,
               'password_error': password_error

               }

    return render(request, 'bank/reset_password.html', context)




def administrator_menu(request):
    users = User.objects.filter(groups__name__in=['Client'])|User.objects.filter(groups__name__in=['SuportClient'])
    paginator = Paginator(users, 10)
    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    try:
        users_page = paginator.page(page)
    except(EmptyPage,InvalidPage):
        users_page = paginator.page(paginator.num_pages)

    context = {'users': users_page,

               }

    return render(request, 'bank/administrator_menu.html', context)


def user_details(request, user_id):

    user = User.objects.get(id=user_id)
    current_user = request.user
    context = {'user': user,
               'current_user':current_user,

               }

    return render(request, 'bank/user_details.html', context)


def edit_user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    number_error = False
    form = EditProfileForm( instance=user)
    profile_form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user)
        if form.is_valid() and profile_form.is_valid():
            form.save()

            usr = form.save(commit=False)

            prf = Profile.objects.filter(user=user)
            profile = prf.get()
            phone = profile_form.cleaned_data['phone']
            company_name = profile_form.cleaned_data['company_name']
            bd = profile_form.cleaned_data['birth_date']
            address = profile_form.cleaned_data['address']
            profile.user = usr
            profile.phone = phone
            profile.company_name = company_name
            profile.birth_date = bd
            profile.address = address


            all_users = User.objects.all()
            for usr in all_users:
                if usr.profile.phone == phone and phone != user.profile.phone:
                    number_error = True

            if number_error == False:

                usr.save()
                profile_form.save()
                profile.save()
                return redirect(administrator_menu)

            else:
                context = {'form': form, 'profile_form': profile_form, 'user':user, 'number_error':number_error}

                return render(request, 'bank/edit_user_profile.html', context)

    else:
        form = EditProfileForm(instance=user)
        profile_form = ProfileForm(instance=user)
        context = {'form': form, 'profile_form':profile_form,  'user':user, 'number_error':number_error}

        return render(request, 'bank/edit_user_profile.html', context)

    context = {'form': form, 'profile_form': profile_form, 'user':user,  'number_error':number_error}

    return render(request, 'bank/edit_user_profile.html', context)



def delete_user(request, user_id):

    user = User.objects.get(id=user_id)
    user.delete()



    return redirect(administrator_menu)


def create_user(request):
    form = SignUpForm(request.POST or None)
    profile_form = ProfileForm(request.POST or None)
    select_from = SimpleForm(request.POST or None)
    if form.is_valid() and profile_form.is_valid() and select_from.is_valid():

        user = form.save(commit=False)
        profile = profile_form.save(commit=False)
        phone = profile_form.cleaned_data['phone']
        user.is_active = True
        profile.user = user
        age_error = profile_form.clean_date_of_birth()

        number_error = False
        all_users = User.objects.all()
        for usr in all_users:
            if usr.profile.phone == phone:
                number_error = True

        if(age_error or number_error):
            context = None
            if age_error == True and number_error ==False:
                context = {
                    "form": form,
                    "profile_form": profile_form,
                    "select_from": select_from,
                    "error_message": "Trebuie sa ai minim 18 ani!"
                }
            elif age_error == False and number_error ==True:
                context = {
                    "form": form,
                    "profile_form": profile_form,
                    "select_from": select_from,
                    "error_message": "Exista deja un cont asociat numarului de telefon!"
                }
            elif age_error == True and number_error ==True:
                context = {
                    "form": form,
                    "profile_form": profile_form,
                    "select_from": select_from,
                    "error_message": "Trebuie sa ai minim 18 ani si exista deja un cont asociat numarului de telefon!"
                }


            return render(request, 'bank/create_user.html', context)
        else:

            user.save()
            profile.save()

            group = Group.objects.get(name=select_from.cleaned_data['choice'])
            user.groups.add(group)

            return redirect(acc_created)

    context = {
        "form": form,
        "profile_form":profile_form,
        "select_from": select_from,
    }
    return render(request, 'bank/create_user.html', context)


def suport_client_menu(request):

    users = User.objects.filter(groups__name__in=['Client'])

    paginator = Paginator(users, 10)

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    try:
        users_page = paginator.page(page)
    except(EmptyPage,InvalidPage):
        users_page = paginator.page(paginator.num_pages)

    context = {'users': users_page,

               }

    return render(request, 'bank/suport_client_menu.html', context)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def change_contract(request, user_id):
    user = User.objects.get(id=user_id)

    profile_form = ContractForm(request.POST, instance=user)
    if request.method == 'POST':
        profile_form = ContractForm(request.POST, instance=user)
        if  profile_form.is_valid():

            prf = Profile.objects.filter(user=user)
            profile = prf.get()
            contract_start_date = profile_form.cleaned_data['contract_start_date']
            contract_end_date = profile_form.cleaned_data['contract_end_date']
            profile.contract_start_date = contract_start_date
            profile.contract_end_date = contract_end_date
            profile.iban = 'RO' + str(random.randint(10,99)) + 'FB24' + id_generator(16, "123456789123456789123456789123456789123456781234567891234567891234567891234567891234567899ABCDEFGHIJKLMNOPQRSTUVWXYZ ")

            profile_form.save()
            profile.save()


            return redirect(suport_client_menu)


    else:

        profile_form = ContractForm(request.POST, instance=user)
        context = { 'profile_form':profile_form}

        return render(request, 'bank/change_contract.html', context)

    context = {'profile_form': profile_form}

    return render(request, 'bank/change_contract.html', context)


def client_menu(request):

    current_user = request.user
    prf = Profile.objects.filter(user=current_user)
    profile = prf.get()
    current_date = datetime.now().date()
    no_contract = False
    expired_contract = False
    if profile.contract_end_date is None or profile.contract_start_date is None:
        no_contract = True


    if profile.contract_start_date is not None and profile.contract_end_date is not None:
        if current_date < profile.contract_start_date or current_date > profile.contract_end_date:
            expired_contract = True



    context = {'no_contract': no_contract,
               'expired_contract': expired_contract,

               }

    return render(request, 'bank/client_menu.html', context)


def new_transaction(request):
    phone_error = False
    amount_error = False
    current_user_error = False
    request.session['transaction_details'] = {}
    form = TransactionForm(request.POST or None)
    transaction_code = random.randint(100000, 999999)


    upd = {'transaction_code': transaction_code}
    request.session['transaction_details'].update(upd)

    if request.method == 'POST':
        form = TransactionForm(request.POST or None)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            amount = form.cleaned_data['amount']
            details = form.cleaned_data['details']
            upd = {'details': details}
            request.session['transaction_details'].update(upd)
            all_users = User.objects.all()

            for usr in all_users:
                if usr.profile.phone == phone:
                    upd = {'identifier': str(phone)}
                    request.session['transaction_details'].update(upd)
                    phone_error = False
                    break
                else:
                    phone_error = True


            if request.user.profile.phone == phone:
                current_user_error = True

            current_user = request.user
            current_user_amont = current_user.profile.amount

            if amount > current_user_amont:
                amount_error = True
            else:
                upd = {'amount': amount}
                request.session['transaction_details'].update(upd)


            upd = {'try': 3}
            request.session['transaction_details'].update(upd)

            if phone_error  or amount_error or current_user_error:

                form = TransactionForm(request.POST or None)
                context = {'form': form,
                           'phone_error':phone_error,
                           'amount_error': amount_error,
                           'current_user_error':current_user_error
                           }

                return render(request, 'bank/new_transaction.html', context)
            else:
                print(transaction_code)
                # current_user_phone_number = request.user.profile.phone
                # to_profile_filter = Profile.objects.filter(phone=phone)
                # to_profile = to_profile_filter.get()
                # to_user = to_profile.user
                # last_name = to_user.last_name
                # first_name = to_user.first_name
                #
                # account_sid = 'ACdf410258a2a7facd104413335b7d44f6'
                # auth_token = 'f6485783cb61ca8860cac9305afda918'
                # client = Client(account_sid, auth_token)
                #
                # message = client.messages \
                #     .create(
                #     body=f"Ati facut o tranzactie in valoare de {amount} RON catre {last_name} {first_name} (nr telefon: {phone}) prin Federal Bank.Codul de confirmare este {transaction_code}",
                #     from_='+12096650211',
                #     to=str(current_user_phone_number)
                # )
                #
                # print(message.sid)
                return redirect(verify_code)


    else:

        form = TransactionForm(request.POST or None)
        context = {'form': form,
                   'phone_error': phone_error,
                   'amount_error': amount_error,
                   'current_user_error': current_user_error

                   }

        return render(request, 'bank/new_transaction.html', context)

    context = {'form': form,
               'phone_error': phone_error,
               'amount_error': amount_error,
               'current_user_error': current_user_error

               }

    return render(request, 'bank/new_transaction.html', context)

def new_transaction_iban(request):
    iban_error = False
    amount_error = False
    current_user_error = False
    request.session['transaction_details'] = {}
    form = TransactionIbanForm(request.POST or None)
    transaction_code = random.randint(100000, 999999)


    upd = {'transaction_code': transaction_code}
    request.session['transaction_details'].update(upd)

    if request.method == 'POST':
        form = TransactionIbanForm(request.POST or None)
        if form.is_valid():
            iban = form.cleaned_data['iban']
            amount = form.cleaned_data['amount']
            details = form.cleaned_data['details']
            upd = {'details': details}
            request.session['transaction_details'].update(upd)
            all_users = User.objects.all()

            for usr in all_users:
                if usr.profile.iban == iban:
                    upd = {'identifier': str(iban)}
                    request.session['transaction_details'].update(upd)
                    iban_error = False
                    break
                else:
                    iban_error = True

            if request.user.profile.iban == iban:
                current_user_error = True


            current_user = request.user
            current_user_amont = current_user.profile.amount

            if amount > current_user_amont:
                amount_error = True
            else:
                upd = {'amount': amount}
                request.session['transaction_details'].update(upd)

            upd = {'try': 3}
            request.session['transaction_details'].update(upd)

            if iban_error  or amount_error or current_user_error:

                form = TransactionIbanForm(request.POST or None)
                context = {'form': form,
                           'phone_error':iban_error,
                           'amount_error': amount_error,
                           'current_user_error': current_user_error
                           }

                return render(request, 'bank/new_transaction_iban.html', context)
            else:
                print(transaction_code)
                # current_user_phone_number = request.user.profile.phone
                # to_profile_filter = Profile.objects.filter(iban=iban)
                # to_profile = to_profile_filter.get()
                # to_user = to_profile.user
                # last_name = to_user.last_name
                # first_name = to_user.first_name
                #
                # account_sid = 'ACdf410258a2a7facd104413335b7d44f6'
                # auth_token = 'f6485783cb61ca8860cac9305afda918'
                # client = Client(account_sid, auth_token)
                #
                # message = client.messages \
                #     .create(
                #     body=f"Ati facut o tranzactie in valoare de {amount} RON catre {last_name} {first_name} (iban: {iban}) prin Federal Bank.Codul de confirmare este {transaction_code}",
                #     from_='+12096650211',
                #     to=str(current_user_phone_number)
                # )
                #
                # print(message.sid)
                return redirect(verify_code)


    else:

        form = TransactionIbanForm(request.POST or None)
        context = {'form': form,
                   'phone_error': iban_error,
                   'amount_error': amount_error,
                   'current_user_error':current_user_error

                   }

        return render(request, 'bank/new_transaction_iban.html', context)

    context = {'form': form,
               'phone_error': iban_error,
               'amount_error': amount_error,
               'current_user_error': current_user_error

               }

    return render(request, 'bank/new_transaction_iban.html', context)



def verify_code(request):

    form = CodeForm(request.POST or None)
    invalid_code = False

    if request.method == 'POST':
        form = CodeForm(request.POST or None)
        if form.is_valid():
            code = form.cleaned_data['code']

            if 'transaction_details' in request.session:
                transaction_details = request.session['transaction_details']

                if str(code) == str(transaction_details['transaction_code']):

                    from_user = request.user
                    prf = Profile.objects.filter(user=from_user)
                    from_profile = prf.get()

                    to_profile_filter = Profile.objects.filter(phone=transaction_details['identifier']) | Profile.objects.filter(iban=transaction_details['identifier'])
                    to_profile = to_profile_filter.get()
                    to_user = to_profile.user

                    amount = transaction_details['amount']
                    details = transaction_details['details']

                    from_profile.amount = from_profile.amount - int(amount)
                    to_profile.amount = to_profile.amount + int(amount)

                    from_profile.save()
                    to_profile.save()


                    Transaction.objects.create(from_user=from_user,to_user=to_user,code=code,amount=amount,details=details)

                    return redirect(client_menu)

                else:
                    invalid_code = True
                    upd = {'try': transaction_details['try'] - 1}
                    request.session['transaction_details'].update(upd)
                    request.session.save()

                    if transaction_details['try']  == 0:
                        return redirect(client_menu)

                    else:

                        form = CodeForm(request.POST or None)
                        context = {'form': form,
                                   'invalid_code': invalid_code,
                                   'tries' : transaction_details['try']
                                   }

                        return render(request, 'bank/verify_code.html', context)



        else:

            form = CodeForm(request.POST or None)
            context = {'form': form,
                       'invalid_code': invalid_code
                       }

            return render(request, 'bank/verify_code.html', context)

    context = {'form': form,
               'invalid_code': invalid_code
               }

    return render(request, 'bank/verify_code.html', context)



def transactions_list(request):




    transactions = Transaction.objects.filter(from_user=request.user).order_by('-date') | Transaction.objects.filter(to_user=request.user).order_by('-date')


    form = DateFilterForm(request.POST or None)
    paginator = Paginator(transactions, 10)

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    try:
        transactions_page = paginator.page(page)
    except(EmptyPage,InvalidPage):
        transactions_page = paginator.page(paginator.num_pages)

    if request.method == 'POST':

        form = DateFilterForm(request.POST or None)
        if form.is_valid():


            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']


            request.session['dates'] = {}
            upd = {'from_date': str(from_date),
                   'to_date': str(to_date),
                   }
            request.session['dates'].update(upd)

            transactions = Transaction.objects.filter(date__gte=from_date,date__lte=to_date,from_user=request.user).order_by('-date')|Transaction.objects.filter(date__gte=from_date,date__lte=to_date,to_user=request.user).order_by('-date')
            paginator = Paginator(transactions, 10)
            try:
                page = int(request.GET.get('page', 1))
            except:
                page = 1

            try:
                transactions_page = paginator.page(page)
            except(EmptyPage, InvalidPage):
                transactions_page = paginator.page(paginator.num_pages)

            context = {'transactions': transactions_page,
                       'form': form,
                       }

            return redirect(transactions_list_filter)
        else:

            form = DateFilterForm(request.POST or None)
            context = {'transactions': transactions_page,
                       'form': form,
                       }

            return render(request, 'bank/transactions_list.html', context)


    context = {'transactions': transactions_page,
               'form': form,
               }

    return render(request, 'bank/transactions_list.html', context)


def transactions_list_filter(request):

    if 'dates' in request.session:
        dates = request.session['dates']
        from_date_datetime = datetime.fromisoformat(dates['from_date'])
        to_date_datetime = datetime.fromisoformat(dates['to_date'])
        transactions = Transaction.objects.filter(date__gte=from_date_datetime, date__lte=to_date_datetime,
                                                  from_user=request.user).order_by(
            '-date') | Transaction.objects.filter(date__gte=from_date_datetime, date__lte=to_date_datetime,
                                                          to_user=request.user).order_by('-date')

        request.session['dates'] = {}
        upd = {'from_date': str(from_date_datetime),
               'to_date': str(to_date_datetime),
               'read': True
               }
        request.session['dates'].update(upd)

    form = DateFilterForm(request.POST or None)
    paginator = Paginator(transactions, 10)

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    try:
        transactions_page = paginator.page(page)
    except(EmptyPage,InvalidPage):
        transactions_page = paginator.page(paginator.num_pages)

    if request.method == 'POST':

        form = DateFilterForm(request.POST or None)
        if form.is_valid():


            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']


            request.session['dates'] = {}
            upd = {'from_date': str(from_date),
                   'to_date': str(to_date),
                   'read': False
                   }
            request.session['dates'].update(upd)

            transactions = Transaction.objects.filter(date__gte=from_date,date__lte=to_date,from_user=request.user).order_by('-date')|Transaction.objects.filter(date__gte=from_date,date__lte=to_date,to_user=request.user).order_by('-date')
            paginator = Paginator(transactions, 10)
            try:
                page = int(request.GET.get('page', 1))
            except:
                page = 1

            try:
                transactions_page = paginator.page(page)
            except(EmptyPage, InvalidPage):
                transactions_page = paginator.page(paginator.num_pages)

            context = {'transactions': transactions_page,
                       'form': form,
                       }

            return render(request, 'bank/transactions_list_filter.html', context)
        else:

            form = DateFilterForm(request.POST or None)
            context = {'transactions': transactions_page,
                       'form': form,
                       }

            return render(request, 'bank/transactions_list_filter.html', context)

    # if "dates" in request.session.keys():
    #     del request.session["dates"]
    #     request.session.modified = True

    context = {'transactions': transactions_page,
               'form': form,
               }

    return render(request, 'bank/transactions_list_filter.html', context)


def deposit(request):
    form = DepositForm(request.POST or None)
    error = False
    if request.method == 'POST':
        form = DepositForm(request.POST or None)
        if form.is_valid():
            error_messages = []

            number = form.cleaned_data['number']
            date = form.cleaned_data['date']
            cv = form.cleaned_data['cv']
            name = form.cleaned_data['name']
            amount = form.cleaned_data['amount']

            try:
                m_string = date[0] + date[1]
                m = int(m_string)
                y_string = '20' + date[3] + date[4]
                y = int(y_string)
                currentMonth = datetime.now().month
                currentYear = datetime.now().year

                current_date = datetime(currentYear, currentMonth, 1)
                contract_date = datetime(y, m, 1)
                if current_date > contract_date:
                    error = True
                    error_messages.append('Cardul este expirat!')


            except Exception as e:
                error = True
                error_messages.append('Data nu este scrisa corect!')



            if (len(number) != 16 ):
                error = True
                error_messages.append('Numarul cardului nu este valid!')
            if not (len(date) == 5 and date[0].isnumeric() and date[1].isnumeric() and date[2] == '/' and date[3].isnumeric() and date[4].isnumeric()):
                error = True
                error_messages.append('Formatul datei nu este valid1 Acesta trebuie sa fie luna/an ex. 01/22')
            if (len(cv) != 3 ):
                error = True
                error_messages.append('Codul CV nu este valid!')
            if not (len(name) > 1 and len(name) < 250) :
                error = True
            if not amount > 0:
                error = True
                error_messages.append('Suma nu poate fi negativa!')


            if error:

                context = {
                           'form': form,
                            'error':error,
                            'error_messages':error_messages
                           }

                return render(request, 'bank/deposit.html', context)
            else:
                user = request.user
                prf = Profile.objects.filter(user=user)
                user_profile = prf.get()

                Transaction.objects.create(from_user=user, to_user=user,code=10000, amount=amount)
                user_profile.amount = user_profile.amount + int(amount)
                user_profile.save()

                return redirect(client_menu)

        else:

            form = DepositForm(request.POST or None)
            context = {
                       'form': form,
                       }

            return render(request, 'bank/deposit.html', context)

    context = {
               'form': form,
               }

    return render(request, 'bank/deposit.html', context)



def transaction_menu(request):

    return render(request, 'bank/transaction_menu.html')