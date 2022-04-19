from django.urls import path, include

from . import views
from .views import all_service_charge, all_transformer_levy
urlpatterns = [
    path('financials/', include(([
        path('resident<int:resident_id>/dashboard/', views.financials_dashboard, name="financials_dashboard"),
        path('sv/payments/<int:payment_id/verify/', views.sv_verification, name="sv_verification"),
        path('resident<int:resident_id>/sv/payments/', views.resident_sv_payments, name="res_sv_payments"),
        path('resident<int:resident_id>/sv/payments/this_month/', views.resident_sv_payments_month,
             name="res_sv_payments_month"),
        path('resident<int:resident_id>/sv/payments/this_year/', views.resident_sv_payments_year,
             name="res_sv_payments_year"),
        path('resident<int:resident_id>/sv/payments/last_year/', views.resident_sv_payments_lastyear,
             name="res_sv_payments_lastyear"),
        path('resident<int:resident_id>/sv/payments/older/', views.resident_sv_payments_older,
             name="res_sv_payments_older"),
        path('service_charge/all/', all_service_charge.as_view(), name='all_service_charge'),
        path('resident<int:resident_id>/tl/payments/', views.resident_tl_payments, name="res_tl_payments"),
        path('resident<int:resident_id>/tl/payments/this_month/', views.resident_tl_payments_month,
             name="res_tl_payments_month"),
        path('resident<int:resident_id>/tl/payments/this_year/', views.resident_tl_payments_year,
             name="res_tl_payments_year"),
        path('resident<int:resident_id>/tl/payments/last_year/', views.resident_tl_payments_lastyear,
             name="res_tl_payments_lastyear"),
        path('resident<int:resident_id>/tl/payments/older/', views.resident_tl_payments_older,
             name="res_tl_payments_older"),
        path('transformer_levy/all/', all_transformer_levy.as_view(), name='all_transformer_levy'),
        path('service_charge/check', views.check_service_charge, name='check_sc'),
        path('transformer_levy/check', views.check_transformer_levy, name='check_tl'),
    ], 'kgera'), namespace='financials')),
]
