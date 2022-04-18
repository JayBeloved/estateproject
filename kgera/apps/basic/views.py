from django.contrib.auth.decorators import login_required
from ..core.decorators import basic_required

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.generic import ListView

from django.core.exceptions import ObjectDoesNotExist


from django.contrib import messages

from django.http.response import HttpResponseRedirect

from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ..structure.models import Houses, Community
from ..residents.models import Residents, Properties
from .models import AccRequest

from .forms import account_request_form, ProfileInfoForm, ProfileInfoUpdateForm, ProfilePicsUpdateForm
from ..residents.forms import ResidentInfoForm, ResidentUpdateForm, NewPropertyForm, EditPropertyForm

from ..financials.models import ResidentFinancialStanding, ServiceChargePayments, TransformerLevyPayments
import datetime

# import string
# import random

###################


class select_house(ListView):
    model = Houses
    template_name = 'basic/dashboards/select_house.html'
    context_object_name = 'houses'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(select_house, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        if query is None:
            all_houses = Houses.objects.all()
            context['searchq'] = all_houses
        else:
            context['searchq'] = query
        return context

    def get_queryset(self):
        queryset = super(select_house, self).get_queryset()
        query = self.request.GET.get('q')
        if query is None:
            return queryset
        else:
            query = query.replace(" ", "+")
            try:
                comm_id = Community.objects.get(commcode=query)
            except ObjectDoesNotExist:
                comm_id = None
            queryset = Houses.objects.filter(
                Q(housecode__icontains=query) | Q(community__exact=comm_id)
            )
            return queryset


def account_request(request, house_id):
    if house_id is None:
        return HttpResponseRedirect(reverse("new_account:select_house"))
    else:
        try:
            house = get_object_or_404(Houses, pk=house_id)
            # Check if there is a current active resident in the house and throw back a error
            if house.housestatus == 1:
                messages.info(request, "House is occupied, cannot add new resident")
                return HttpResponseRedirect(reverse("new_account:select_house"))
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("new_account:select_house"))

    # Create Resident
    form = account_request_form(request.POST or None)

    # Get form data
    if request.method == "POST":

        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            p_word1 = form.cleaned_data.get("password1")
            p_word2 = form.cleaned_data.get("password2")

            if Residents.objects.filter(resident_email=email).exist():
                messages.error(request, f'Email already in use by another Resident. Use a unique email address')
                return redirect(request, 'new_account:account_request', {'form': form})
            else:

                if p_word1 == p_word2:

                    house = Houses.objects.get(id=house_id)
                    rq = AccRequest.objects.create(house=house, first_name=first_name,
                                                   last_name=last_name, email=email, password=p_word1)
                    rq.save()

                    return redirect('new_account:request_success')
                else:
                    form = form
                    messages.error(request, 'The Passwords did not match')
                    return redirect(request, 'new_account:account_request', {'form': form})

        else:
            return redirect('new_account:request_error')

    context = {
        'house': house,
        'form': form
    }

    return render(request, 'basic/dashboards/new_request.html', context)


def request_success(request):
    return render(request, 'basic/dashboards/request_success.html')


def request_error(request):
    return render(request, 'basic/dashboards/request_error.html')


@login_required()
@basic_required()
def resident_dashboard(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("landing"))

    # New Property Form
    prop_form = NewPropertyForm(request.POST or None)

    if request.method == 'POST':

        if prop_form.is_valid():
            resident = sel_resident
            property_type = prop_form.cleaned_data.get("prop_type")
            property_desc = prop_form.cleaned_data.get("prop_desc")

            # Generate Property Code
            def gen_prop_code():
                # Get Number of Property of that type Owned by the Resident o
                get_prop = Properties.objects.filter(resident=resident, property_type=property_type).__len__()
                if get_prop == 0:
                    return f"{resident.resident_code}/{property_type}/01"
                else:
                    get_prop += 1
                    return f"{resident.resident_code}/{property_type}/0{get_prop}"

            prop_code = gen_prop_code()
            property_code = prop_code
            while Properties.objects.filter(property_code=prop_code):
                prop_code = gen_prop_code()
                if not Properties.objects.filter(property_code=gen_prop_code):
                    property_code = gen_prop_code

            pt = Properties.objects.create(resident=resident, property_type=property_type,
                                           property_desc=property_desc,
                                           property_code=property_code)
            pt.save()
            messages.success(request, 'Property Registered Successfully')
            properties = Properties.objects.filter(resident=resident)
        else:
            messages.error(request, 'Error Validating The Form')
            messages.info(request, prop_form.errors)

    info_form = ResidentInfoForm(instance=sel_resident)
    properties = Properties.objects.filter(resident=sel_resident)
    prop_count = properties.__len__()

    context = {
        'prop_form': prop_form,
        'form': info_form,
        'resident': sel_resident,
        'properties': properties,
        'prop_count': prop_count,
    }
    return render(request, 'basic/dashboards/resident_dashboard.html', context)


@login_required()
@basic_required()
def service_charge_dashboard(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))

    # Get Data for context
    sv_count = ServiceChargePayments.objects.filter(resident=sel_resident).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(service_charge_payments, 10)
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

    return render(request, 'basic/all/res_sv_financials.html', context)


@login_required()
@basic_required()
def sv_payments_month(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))
    # Get Data for context
    sv_count = ServiceChargePayments.objects.filter \
        (resident=sel_resident, payment_date__year=datetime.date.today().year,
         payment_date__month=datetime.date.today().month).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1,
                                                            payment_date__year=datetime.date.today().year,
                                                            payment_date__month=datetime.date.today().month))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident,
                                             payment_date__year=datetime.date.today().year,
                                             payment_date__month=datetime.date.today().month).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(service_charge_payments, 10)
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

    return render(request, 'basic/all/res_sv_financials.html', context)


@login_required()
@basic_required()
def sv_payments_year(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))
    # Get Data for context
    sv_count = ServiceChargePayments.objects.filter\
        (resident=sel_resident, payment_date__year=datetime.date.today().year).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1,
                                                            payment_date__year=datetime.date.today().year))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident,
                                             payment_date__year=datetime.date.today().year).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(service_charge_payments, 10)
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

    return render(request, 'basic/all/res_sv_financials.html', context)


@login_required()
@basic_required()
def sv_payments_lastyear(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))

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

    page = request.GET.get('page', 1)
    paginator = Paginator(service_charge_payments, 10)
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

    return render(request, 'basic/all/res_sv_financials.html', context)


@login_required()
@basic_required()
def sv_payments_older(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))
    # Get Data for context
    # Get last year value
    last_year = datetime.date.today().year - 1
    sv_count = ServiceChargePayments.objects.filter(resident=sel_resident,
                                                    payment_date__lte=datetime.date(last_year, 1, 1)).__len__()
    sv_count_ver = len(ServiceChargePayments.objects.filter(resident=sel_resident, status=1,
                                                            payment_date__lte=datetime.date(last_year, 1, 1)))
    service_charge_payments = \
        ServiceChargePayments.objects.filter(resident=sel_resident,
                                             payment_date__lte=datetime.date(last_year, 1, 1)).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(service_charge_payments, 10)
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

    return render(request, 'basic/all/res_sv_financials.html', context)


#################################################################################################
@login_required()
@basic_required()
def Transformer_levy_dashboard(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))

    # Get Data for context
    tl_count = TransformerLevyPayments.objects.filter(resident=sel_resident).__len__()
    tl_count_ver = len(TransformerLevyPayments.objects.filter(resident=sel_resident, status=1))
    transformer_levy_payments = \
        TransformerLevyPayments.objects.filter(resident=sel_resident).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(transformer_levy_payments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': tl_count,
        'count_ver': tl_count_ver,
        'payments': payments,
    }

    return render(request, 'basic/all/res_tl_financials.html', context)


@login_required()
@basic_required()
def tl_payments_month(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))

    # Get Data for context
    tl_count = TransformerLevyPayments.objects.filter\
        (resident=sel_resident, payment_date__year=datetime.date.today().year,
         payment_date__month=datetime.date.today().month).__len__()
    tl_count_ver = len(TransformerLevyPayments.objects.filter(resident=sel_resident, status=1,
                                                              payment_date__year=datetime.date.today().year,
                                                              payment_date__month=datetime.date.today().month))
    transformer_levy_payments = \
        TransformerLevyPayments.objects.filter(resident=sel_resident,
                                               payment_date__year=datetime.date.today().year,
                                               payment_date__month=datetime.date.today().month).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(transformer_levy_payments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': tl_count,
        'count_ver': tl_count_ver,
        'payments': payments,
    }

    return render(request, 'basic/all/res_tl_financials.html', context)


@login_required()
@basic_required()
def tl_payments_year(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))

    # Get Data for context
    tl_count = TransformerLevyPayments.objects.filter \
        (resident=sel_resident, payment_date__year=datetime.date.today().year).__len__()
    tl_count_ver = len(TransformerLevyPayments.objects.filter(resident=sel_resident, status=1,
                                                              payment_date__year=datetime.date.today().year))
    transformer_levy_payments = \
        TransformerLevyPayments.objects.filter(resident=sel_resident,
                                               payment_date__year=datetime.date.today().year).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(transformer_levy_payments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': tl_count,
        'count_ver': tl_count_ver,
        'payments': payments,
    }

    return render(request, 'basic/all/res_tl_financials.html', context)


@login_required()
@basic_required()
def tl_payments_lastyear(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))

    # Get Data for context
    # Get last year value
    last_year = datetime.date.today().year - 1
    tl_count = TransformerLevyPayments.objects.filter(resident=sel_resident,
                                                      payment_date__year=last_year).__len__()
    tl_count_ver = len(TransformerLevyPayments.objects.filter(resident=sel_resident, status=1,
                                                              payment_date__year=last_year))
    transformer_levy_payments = \
        TransformerLevyPayments.objects.filter(resident=sel_resident,
                                               payment_date__year=last_year).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(transformer_levy_payments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': tl_count,
        'count_ver': tl_count_ver,
        'payments': payments,
    }

    return render(request, 'basic/all/res_tl_financials.html', context)


@login_required()
@basic_required()
def tl_payments_older(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))

    # Get Data for context
    # Get last year value
    last_year = datetime.date.today().year - 1
    tl_count = TransformerLevyPayments.objects.filter(resident=sel_resident,
                                                      payment_date__lte=datetime.date(last_year, 1, 1)).__len__()
    tl_count_ver = len(TransformerLevyPayments.objects.filter(resident=sel_resident, status=1,
                                                              payment_date__lte=datetime.date(last_year, 1, 1)))
    transformer_levy_payments = \
        TransformerLevyPayments.objects.filter(resident=sel_resident,
                                               payment_date__lte=datetime.date(last_year, 1, 1)).order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(transformer_levy_payments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)

    context = {
        'resident': sel_resident,
        'count': tl_count,
        'count_ver': tl_count_ver,
        'payments': payments,
    }

    return render(request, 'basic/all/res_tl_financials.html', context)


###############################################################################################################


@login_required()
@basic_required()
def update_info(request):
    try:
        sel_resident = Residents.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Something Went Wrong \n'
                                'There is no Resident Data attached to this account.')
        return HttpResponseRedirect(reverse("landing"))

    if request.method == 'POST':
        u_form = ResidentUpdateForm(request.POST, instance=sel_resident)
        if u_form.is_valid():

            if Residents.objects.filter(resident_email=u_form.cleaned_data.get('resident_email')).exists():
                messages.error(request, f'Email already in use by another Resident. Use a unique email address')
            elif Residents.objects.filter(mobile_number=u_form.cleaned_data.get('mobile_number')).exists():
                messages.error(request, f'Mobile Number already in use by another Resident.')
            else:
                u_form.save()
                messages.success(request, 'Resident Detail Update Successful')
            return redirect('resident_account:resident_dashboard')
        else:
            messages.error(request, 'Something Went Wrong, Unable to update Resident Details')
            messages.info(request, u_form.errors)
    else:
        u_form = ResidentUpdateForm(instance=sel_resident)
    context = {
        'form': u_form,
        'resident': sel_resident
    }

    return render(request, 'basic/dashboards/update_resident.html', context)


def edit_property(request, property_id):
    if property_id is None:
        messages.error(request, 'No Property Selected')
        return HttpResponseRedirect(reverse("resident_account:resident_dashboard"))
    else:
        try:
            sel_resident = Residents.objects.get(user=request.user)
            sel_property = Properties.objects.get(id=property_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong \n'
                                    'There is no Resident Data attached to this account.')
            return HttpResponseRedirect(reverse("landing"))

    if request.method == 'POST':
        u_form = EditPropertyForm(request.POST, instance=sel_property)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Property Edit Successful')
            return redirect('resident_account:resident_dashboard')
        else:
            messages.error(request, 'Something Went Wrong, Unable to update Resident Details')
            messages.info(request, u_form.errors)
    else:
        u_form = EditPropertyForm(instance=sel_property)
    context = {
        'form': u_form,
        'resident': sel_resident,
        'property': sel_property
    }

    return render(request, 'basic/dashboards/update_properties.html', context)


# PROFILE VIEWS #################################################
@login_required()
@basic_required()
def profile(request):
    get_usertype = request.user.user_type
    if get_usertype == 1:
        usertype = 'Administrator'
    elif get_usertype == 2:
        usertype = 'Secretary'
    else:
        usertype = 'Basic User'

    info_form = ProfileInfoForm(instance=request.user)
    return render(request, 'basic/dashboards/profile.html', {'form': info_form, 'usertype': usertype})


@login_required()
@basic_required()
def profile_info(request):
    if request.method == 'POST':
        u_form = ProfileInfoUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('profile:profile_info')
        else:
            messages.error(request, 'Something Went Wrong, Unable to update profile')
    else:
        u_form = ProfileInfoUpdateForm(instance=request.user)

    return render(request, 'basic/dashboards/profile_details.html', {'form': u_form})


@login_required()
@basic_required()
def profile_pics(request):
    if request.method == 'POST':
        p_form = ProfilePicsUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Profile Picture Updated Successfully')
            return redirect('resident_account:profile_picture')
        else:
            messages.error(request, 'Something Went Wrong, Unable to update profile picture')
    else:
        p_form = ProfilePicsUpdateForm(instance=request.user.profile)

    return render(request, 'basic/dashboards/profile_pics.html', {'form': p_form})


@login_required()
@basic_required()
def profile_password(request):
    return render(request, 'basic/dashboards/profile_pword.html')
