import datetime

from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required
from ..core.decorators import admin_required

from django.db.models import Q
from django.views.generic import ListView

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import messages

from django.http.response import HttpResponseRedirect, HttpResponse

from django.urls import reverse

from .models import *
from ..structure.models import Community, Houses
from ..residents.models import Residents
from .forms import Pay_Service_ChargeForm, Pay_Transformer_LevyForm, SearchForm

import random
import string


@login_required()
@admin_required()
def financials_dashboard(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_residents"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_residents"))
        try:
            financial_standing = ResidentFinancialStanding.objects.get(resident=sel_resident.resident_code)
        except ObjectDoesNotExist:
            messages.error(request, 'Resident Financial Standing Yet To Updated \n'
                                    'Resident Financial Dashboard Un-available.')
            return HttpResponseRedirect(reverse("residents:all_residents"))

    # Payment Form
    p_form = Pay_Service_ChargeForm(request.POST or None)
    t_form = Pay_Transformer_LevyForm(request.POST or None)

    if request.POST.get('formId') == '1':
        if p_form.is_valid():
            pay_resident = p_form.cleaned_data.get("resident")
            payment_date = p_form.cleaned_data.get("payment_date")
            amount = p_form.cleaned_data.get("amount")
            payment_note = p_form.cleaned_data.get("payment_note")
            status = 0

            def gen_ref():
                house_code = sel_resident.house.housecode
                hs = house_code.replace("/", "")
                dt = payment_date.year

                # Generate Random Characters
                char1 = random.choice(string.ascii_uppercase)
                char2 = random.choice(string.ascii_lowercase)
                char3 = random.choice(string.digits)
                char4 = random.choice(string.hexdigits)
                char5 = random.choice(string.ascii_letters)

                return f"KGERA/{dt}/SV/{hs}/{char1}{char2}{char3}{char4}{char5}/rsd{sel_resident.id}"

            ref = gen_ref()
            payment_ref = ref
            while ServiceChargePayments.objects.filter(payment_ref=ref):
                ref = gen_ref()
                if not ServiceChargePayments.objects.filter(payment_ref=gen_ref):
                    payment_ref = gen_ref

            pay = ServiceChargePayments.objects.create(resident=sel_resident, payment_date=payment_date, amount=amount,
                                                       payment_note=payment_note, payment_ref=payment_ref,
                                                       status=status)
            pay.save()
            messages.success(request, "Payment Submitted Successfully. \n "
                                      "You will be notified once payment is verified.")

            # Re-query Context
            sv_count = ServiceChargePayments.objects.filter(resident=sel_resident).__len__()
            service_charge_payments = \
                ServiceChargePayments.objects.filter(resident=sel_resident).order_by('-id')

        else:
            messages.error(request, 'Error validating the form')
            messages.info(request, p_form.errors)
        return redirect('financials:financials_dashboard', sel_resident.id)

    elif request.POST.get('formId') == '2':
        if t_form.is_valid():
            pay_resident = t_form.cleaned_data.get("resident")
            payment_date = t_form.cleaned_data.get("payment_date")
            amount = t_form.cleaned_data.get("amount")
            payment_note = t_form.cleaned_data.get("payment_note")
            status = 0

            def gen_ref():
                house_code = sel_resident.house.housecode
                hs = house_code.replace("/", "")
                dt = payment_date.year

                # Generate Random Characters
                char1 = random.choice(string.ascii_uppercase)
                char2 = random.choice(string.ascii_lowercase)
                char3 = random.choice(string.digits)
                char4 = random.choice(string.hexdigits)
                char5 = random.choice(string.ascii_letters)

                return f"KGERA/{dt}/SV/{hs}/{char1}{char2}{char3}{char4}{char5}/rsd{sel_resident.id}"

            ref = gen_ref()
            payment_ref = ref
            while TransformerLevyPayments.objects.filter(payment_ref=ref):
                ref = gen_ref()
                if not TransformerLevyPayments.objects.filter(payment_ref=gen_ref):
                    payment_ref = gen_ref

            pay = TransformerLevyPayments.objects.create(resident=sel_resident, payment_date=payment_date,
                                                         amount=amount, payment_note=payment_note,
                                                         payment_ref=payment_ref,
                                                         status=status)
            pay.save()
            messages.success(request, "Payment Submitted Successfully. \n "
                                      "You will be notified once payment is verified.")

            # Re-query Context
            tl_count = TransformerLevyPayments.objects.filter(resident=sel_resident).__len__()
            transformer_levy_payments = \
                TransformerLevyPayments.objects.filter(resident=sel_resident).order_by('-id')

        else:
            messages.error(request, 'Error validating the form')
            messages.info(request, t_form.errors)
        return redirect('financials:financials_dashboard', sel_resident.id)

    # Get Data For Context
    sv_count = ServiceChargePayments.objects.filter(resident=sel_resident).__len__()
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident).order_by('-id')

    tl_count = TransformerLevyPayments.objects.filter(resident=sel_resident).__len__()
    transformer_levy_payments = \
        TransformerLevyPayments.objects.filter(resident=sel_resident).order_by('-id')

    context = {
        'resident': sel_resident,
        'sv_count': sv_count,
        'sv_payments': service_charge_payments,
        'tl_count': tl_count,
        'tl_payments': transformer_levy_payments,
        'standing': financial_standing,
        'p_form': p_form,
        't_form': t_form,

    }

    return render(request, 'financials/dashboards/financials.html', context)


def resident_sv_payments(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_service_charge"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))
        try:
            financial_standing = ResidentFinancialStanding.objects.get(resident=sel_resident.resident_code)
        except ObjectDoesNotExist:
            messages.error(request, 'Resident Financial Standing Yet To Updated \n'
                                    'Resident Financial Dashboard Un-available.')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))

    # Get Data for context
    sv_count = ServiceChargePayments.objects.filter(resident=sel_resident).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident).order_by('-id')

    page = request.Get.get('page', 1)
    paginator = Paginator(ServiceChargePayments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': sv_count,
        'count_ver': sv_count_ver,
        'payments': payments,
    }

    return render(request, 'financials/dashboards/res_sv_financials.html', context)


def resident_sv_payments_month(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_service_charge"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))
        try:
            financial_standing = ResidentFinancialStanding.objects.get(resident=sel_resident.resident_code)
        except ObjectDoesNotExist:
            messages.error(request, 'Resident Financial Standing Yet To Updated \n'
                                    'Resident Financial Dashboard Un-available.')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))

    # Get Data for context
    sv_count = ServiceChargePayments.objects.filter\
        (resident=sel_resident, payment_date__month=datetime.date.today().month).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1,
                                                            payment_date__month=datetime.date.today().month))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident,
                                             payment_date__month=datetime.date.today().month).order_by('-id')

    page = request.Get.get('page', 1)
    paginator = Paginator(ServiceChargePayments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': sv_count,
        'count_ver': sv_count_ver,
        'payments': payments,
    }

    return render(request, 'financials/dashboards/res_sv_financials.html', context)


def resident_sv_payments_year(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_service_charge"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))
        try:
            financial_standing = ResidentFinancialStanding.objects.get(resident=sel_resident.resident_code)
        except ObjectDoesNotExist:
            messages.error(request, 'Resident Financial Standing Yet To Updated \n'
                                    'Resident Financial Dashboard Un-available.')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))

    # Get Data for context
    sv_count = ServiceChargePayments.objects.filter\
        (resident=sel_resident, payment_date__year=datetime.date.today().year).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1,
                                                            payment_date__year=datetime.date.today().year))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident,
                                             payment_date__year=datetime.date.today().year).order_by('-id')

    page = request.Get.get('page', 1)
    paginator = Paginator(ServiceChargePayments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': sv_count,
        'count_ver': sv_count_ver,
        'payments': payments,
    }

    return render(request, 'financials/dashboards/res_sv_financials.html', context)


def resident_sv_payments_lastyear(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_service_charge"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))
        try:
            financial_standing = ResidentFinancialStanding.objects.get(resident=sel_resident.resident_code)
        except ObjectDoesNotExist:
            messages.error(request, 'Resident Financial Standing Yet To Updated \n'
                                    'Resident Financial Dashboard Un-available.')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))

    # Get Data for context
    # Get last year value
    last_year = datetime.date.today().year - 1
    sv_count = ServiceChargePayments.objects.filter(resident=sel_resident,
                                                    payment_date__year=last_year).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1,
                                                            payment_date__year=last_year))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident,
                                             payment_date__year=last_year).order_by('-id')

    page = request.Get.get('page', 1)
    paginator = Paginator(ServiceChargePayments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': sv_count,
        'count_ver': sv_count_ver,
        'payments': payments,
    }

    return render(request, 'financials/dashboards/res_sv_financials.html', context)


def resident_sv_payments_older(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_service_charge"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))
        try:
            financial_standing = ResidentFinancialStanding.objects.get(resident=sel_resident.resident_code)
        except ObjectDoesNotExist:
            messages.error(request, 'Resident Financial Standing Yet To Updated \n'
                                    'Resident Financial Dashboard Un-available.')
            return HttpResponseRedirect(reverse("residents:all_service_charge"))

    # Get Data for context
    sv_count = ServiceChargePayments.objects.filter\
        (resident=sel_resident, payment_date__year=datetime.date.today().year).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1,
                                                            payment_date__year=datetime.date.today().year))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident,
                                             payment_date__year=datetime.date.today().year).order_by('-id')

    page = request.Get.get('page', 1)
    paginator = Paginator(ServiceChargePayments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': sv_count,
        'count_ver': sv_count_ver,
        'payments': payments,
    }

    return render(request, 'financials/dashboards/res_sv_financials.html', context)


class all_service_charge(ListView):
    model = ServiceChargePayments
    template_name = 'financials/all/all_service_charge.html'
    context_object_name = 'payments'
    paginate_by = 6
    extra_context = {
        'form': SearchForm,
    }

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(all_service_charge, self).get_context_data(**kwargs)
        query1 = self.request.GET.get('q1')
        query2 = self.request.GET.get('q2')

        if query1 is None and query2 is None:
            allservicecharge = ServiceChargePayments.objects.all()
            context['searchq1'] = allservicecharge
        else:
            context['searchq1'] = query1
            context['searchq2'] = query2
        return context

    def get_queryset(self):
        queryset = super(all_service_charge, self).get_queryset()
        query1 = self.request.GET.get('q1')
        query2 = self.request.GET.get('q2')

        if query1 is None and query2 is None:
            return queryset
        else:
            if query1 is not None:
                query1 = query1.replace(" ", "+")
            if query2 is not None:
                query2 = query2.replace(" ", "+")

            try:
                house = Houses.objects.get(id=query1).housecode
                house_code = house.replace("/", "")
            except ObjectDoesNotExist:
                house = None
                house_code = None
            except ValueError:
                house = None
                house_code = None
            ############################
            try:
                rsd = Residents.objects.get(id=int(query2)).resident_code
            except ObjectDoesNotExist:
                rsd = None
            except ValueError:
                rsd = None
            ###############################

            if house_code is not None:
                queryset = ServiceChargePayments.objects.filter(
                    Q(payment_ref__icontains=house_code)
                )
            elif rsd is not None:
                queryset = ServiceChargePayments.objects.filter(
                    Q(resident=rsd)
                )

            return queryset


class all_transformer_levy(ListView):
    model = TransformerLevyPayments
    template_name = 'financials/all/all_transformer_levy.html'
    context_object_name = 'payments'
    paginate_by = 6
    extra_context = {
        'form': SearchForm,
    }

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(all_transformer_levy, self).get_context_data(**kwargs)
        query1 = self.request.GET.get('q1')
        query2 = self.request.GET.get('q2')

        if query1 is None and query2 is None:
            alltransformerlevy = TransformerLevyPayments.objects.all()
            context['searchq'] = alltransformerlevy
        else:
            context['searchq1'] = query1
            context['searchq2'] = query2
        return context

    def get_queryset(self):
        queryset = super(all_transformer_levy, self).get_queryset()
        query1 = self.request.GET.get('q1')
        query2 = self.request.GET.get('q2')

        if query1 is None and query2 is None:
            return queryset
        else:
            if query1 is not None:
                query1 = query1.replace(" ", "+")
            if query2 is not None:
                query2 = query2.replace(" ", "+")

            try:
                house = Houses.objects.get(id=query1).housecode
                house_code = house.replace("/", "")
            except ObjectDoesNotExist:
                house = None
                house_code = None
            except ValueError:
                house = None
                house_code = None
            ############################
            try:
                rsd = Residents.objects.get(id=int(query2)).resident_code
            except ObjectDoesNotExist:
                rsd = None
            except ValueError:
                rsd = None
            ###############################

            if house_code is not None:
                queryset = TransformerLevyPayments.objects.filter(
                    Q(payment_ref__icontains=house_code)
                )
            elif rsd is not None:
                queryset = TransformerLevyPayments.objects.filter(
                    Q(resident=rsd)
                )

            return queryset


def check_service_charge(request):
    sv_count = ServiceChargePayments.objects.all()

    if len(sv_count) == 0:
        return render(request, 'financials/all/no_sc.html')
    else:
        return redirect('financials:all_service_charge')


def check_transformer_levy(request):
    tl_count = TransformerLevyPayments.objects.all()

    if len(tl_count) == 0:
        return render(request, 'financials/all/no_tl.html')
    else:
        return redirect('financials:all_transformer_levy')
