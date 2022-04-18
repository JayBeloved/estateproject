from django.urls import path, include

from . import views

from .views import select_house

urlpatterns = [
    path('new_account/', include(([
        path('select_house/', select_house.as_view(), name="select_house"),
        path('account_request/house<int:house_id>/', views.account_request, name="account_request"),
        path('success', views.request_success, name="request_success"),
        path('error', views.request_error, name="request_error"),
    ], 'kgera'), namespace="new_account")),

    path('resident/', include(([
            path('dashboard/', views.resident_dashboard, name="resident_dashboard"),
            path('update/primary_details/', views.update_info, name="update_info"),
            path('properties/property<int:property_id>/edit', views.edit_property,
                 name="edit_property"),
            path('sv/payments/', views.service_charge_dashboard, name="sv_payments"),
            path('sv/payments/this_month/', views.sv_payments_month, name="sv_payments_month"),
            path('sv/payments/this_year/', views.sv_payments_year, name="sv_payments_year"),
            path('sv/payments/last_year/', views.sv_payments_lastyear, name="sv_payments_lastyear"),
            path('sv/payments/older/', views.sv_payments_older, name="sv_payments_older"),
            path('tl/payments/', views.Transformer_levy_dashboard, name="tl_payments"),
            path('tl/payments/this_month/', views.tl_payments_month, name="tl_payments_month"),
            path('tl/payments/this_year/', views.tl_payments_year, name="tl_payments_year"),
            path('tl/payments/last_year/', views.tl_payments_lastyear, name="tl_payments_lastyear"),
            path('tl/payments/older/', views.tl_payments_older, name="tl_payments_older"),

        ], 'kgera'), namespace="resident_account")),

    path('user/', include(([
            path('profile/', views.profile, name="profile"),
            path('update/profile_picture', views.profile_pics, name="profile_picture"),
            path('update/profile_info/', views.profile_info, name="profile_info"),
            path('update/password_reset/', views.profile_password, name="password_reset"),
        ], 'kgera'), namespace='resident_profile')),
    ]

