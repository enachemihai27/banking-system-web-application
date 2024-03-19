from django.urls import path, include
from .import views



urlpatterns = [
    path('', views.index, name='index'),
    path("login", views.login_usr, name='login'),
    path("logout", views.logout_usr, name='logout'),
    path('register', views.register, name="register"),
    path("account_created", views.acc_created, name='acc_created'),
    path("profile", views.profile, name='profile'),
    path("profile/edit", views.edit_profile, name='edit_profile'),
    path("change-password", views.change_password, name='change_password'),
    path("change-password-done", views.password_changed, name='password_changed'),
    path("reset-password/<int:user_id>", views.reset_password, name='reset_password'),
    path("administrator-menu", views.administrator_menu, name='administrator_menu'),
    path("suport-client-menu", views.suport_client_menu, name='suport_client_menu'),
    path("client-menu", views.client_menu, name='client_menu'),
    path("transaction-menu", views.transaction_menu, name='transaction_menu'),
    path("new-transaction", views.new_transaction, name='new_transaction'),
    path("new-transaction-iban", views.new_transaction_iban, name='new_transaction_iban'),
    path("verify-code", views.verify_code, name='verify_code'),
    path("verify-login", views.verify_login, name='verify_login'),
    path("transaction-list", views.transactions_list, name='transactions_list'),
    path("transaction-list-filter", views.transactions_list_filter, name='transactions_list_filter'),
    path("deposit", views.deposit, name='deposit'),
    path('detalii-user/<int:user_id>', views.user_details, name='user_details'),
    path('edit-user-profile/<int:user_id>', views.edit_user_profile, name='edit_user_profile'),
    path('delete-user/<int:user_id>', views.delete_user, name='delete_user'),
    path('create-user', views.create_user, name='create_user'),
    path('change-contract/<int:user_id>', views.change_contract, name='change_contract'),

]
