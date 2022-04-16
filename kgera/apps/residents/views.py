from django.contrib.auth.decorators import login_required
from ..core.decorators import admin_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.generic import ListView

from django.core.exceptions import ObjectDoesNotExist


from django.contrib import messages

from django.http.response import HttpResponseRedirect, HttpResponse

from django.urls import reverse

from ..basic.models import AccRequest
from ..structure.models import Houses, Community
from .models import Residents, Properties, CommunityHeads
from ..financials.models import ResidentFinancialStanding, ServiceChargePayments, TransformerLevyPayments
from ..accounts.models import User, Profile

from .forms import NewResidentForm, ResidentInfoForm, \
    ResidentUpdateForm, NewPropertyForm, EditPropertyForm

import string
import random


# Create your views here.

@login_required()
@admin_required()
def residents_dashboard(request):
    # Get data for counters
    activeresidents = Residents.objects.filter(occupancy_status=1)
    vacatedresidents = Residents.objects.filter(occupancy_status=0)
    communityheads = CommunityHeads.objects.filter(appointment_status=1)
    properties = Properties.objects.all()

    # Get Data Count
    activeresidents_count = activeresidents.count()
    vacatedresidents_count = vacatedresidents.count()
    activecommunity_heads = communityheads.count()
    property_count = properties.count()

    # Get Numbered list for table
    residents = Residents.objects.filter(occupancy_status=1).order_by('-id')[:6]

    context = {
        'activeresidents_count': activeresidents_count,
        'vacatedresidents_count': vacatedresidents_count,
        'activecommunity_heads': activecommunity_heads,
        'property_count': property_count,
        'residents': residents,
    }

    return render(request, 'residents/dashboards/residents.html', context)


class select_house(ListView):
    model = Houses
    template_name = 'residents/dashboards/get_house.html'
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


@login_required()
@admin_required()
def newresident_dashboard(request, house_id):
    if house_id is None:
        return HttpResponseRedirect(reverse("residents:select_house"))
    else:
        try:
            house = get_object_or_404(Houses, pk=house_id)
            # Check if there is a current active resident in the house and throw back a error
            if house.housestatus == 1:
                messages.info(request, "House is occupied, cannot add new resident")
                return HttpResponseRedirect(reverse("residents:select_house"))
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:select_house"))

    # Create Resident
    form = NewResidentForm(request.POST or None)

    # Get form data
    if request.method == "POST":

        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            mobile = form.cleaned_data.get("mobile")
            occ_start = form.cleaned_data.get("occ_start")
            status = form.cleaned_data.get("status")

            if Residents.objects.filter(resident_email=email).exist():
                messages.error(request, f'Email already in use by another Resident. Use a unique email address')
            elif Residents.objects.filter(mobile_number=mobile).exists():
                messages.error(request, f'Mobile Number already in use by another Resident.')
            else:
                resident_code = 0

                # Generate Unique Resident Code
                # Randomly Choose Letters for adding to code
                def gencode():
                    char1 = random.choice(string.ascii_uppercase)
                    char2 = random.choice(string.ascii_lowercase)
                    char3 = random.choice(string.ascii_letters)
                    char4 = random.choice('1234567890')
                    char5 = random.choice(string.ascii_uppercase)
                    char6 = random.choice(string.ascii_lowercase)
                    char7 = random.choice(string.ascii_letters)

                    return f"rsd/{char1}{char2}{char3}-{char4}{char5}/{char6}{char7}"

                rsd = gencode()
                resident_code = rsd
                while Residents.objects.filter(resident_code=rsd):
                    rsd = gencode()
                    if not Residents.objects.filter(resident_code=gencode):
                        resident_code = gencode

                rs = Residents.objects.create(house=house, resident_code=resident_code, first_name=first_name,
                                          last_name=last_name, resident_email=email, mobile_number=mobile,
                                          occupancy_start=occ_start, occupancy_status=status)
                rs.save()
                if house.housestatus == 0:
                    house.housestatus = 1
                    house.save()
                messages.success(request, f'Resident {resident_code}-{first_name} {last_name} Added Successfully')

        else:
            messages.error(request, 'Error validating the form')
            messages.info(request, form.errors)
        return HttpResponseRedirect(reverse("residents:residents_dashboard"))

    context = {
        'house': house,
        'form': form
    }

    return render(request, 'residents/dashboards/new_resident.html', context)


class all_residents(ListView):
    model = Residents
    template_name = 'residents/all/all_residents.html'
    context_object_name = 'residents'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(all_residents, self).get_context_data(**kwargs)
        query1 = self.request.GET.get('q1')
        query2 = self.request.GET.get('q2')

        if query1 is None and query2 is None:
            allresidents = Residents.objects.all()
            context['searchq'] = allresidents
        else:
            context['searchq1'] = query1
            context['searchq2'] = query2
        return context

    def get_queryset(self):
        queryset = super(all_residents, self).get_queryset()
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
                comm_id = Community.objects.get(commcode=query1)
            except ObjectDoesNotExist:
                comm_id = None

            try:
                house_id = Houses.objects.get(housecode=query1)
            except ObjectDoesNotExist:
                house_id = None
            except ValueError:
                house_id = None

            if comm_id is not None:
                filtered_residents = Residents.objects.filter(house__community=comm_id)

                queryset = filtered_residents.filter(
                    Q(first_name__icontains=query2) | Q(last_name__icontains=query2)
                )
            elif house_id is not None:
                queryset = Residents.objects.filter(
                    Q(house__exact=house_id)
                )
            else:
                queryset = Residents.objects.filter(
                    Q(first_name__icontains=query2) | Q(last_name__icontains=query2)
                )

            return queryset


@login_required()
@admin_required()
def residents_info(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_residents"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_residents"))

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

        # Financials
        sv_count = ServiceChargePayments.objects.filter(resident=sel_resident.resident_code).__len__()
        service_charge_payments = \
            ServiceChargePayments.objects.filter(resident=sel_resident.resident_code).order_by('id')[:3]

        tl_count = TransformerLevyPayments.objects.filter(resident=sel_resident.resident_code).__len__()
        transformer_levy_payments = \
            TransformerLevyPayments.objects.filter(resident=sel_resident.resident_code).order_by('id')[:3]

        context = {
            'prop_form': prop_form,
            'form': info_form,
            'resident': sel_resident,
            'properties': properties,
            'prop_count': prop_count,
            'sv_count': sv_count,
            'sv_payments': service_charge_payments,
            'tl_count': tl_count,
            'tl-payments': transformer_levy_payments,
        }
        return render(request, 'residents/dashboards/resident_info.html', context)


@login_required()
@admin_required()
def update_resident_info(request, resident_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_residents"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_residents"))

        if request.method == 'POST':
            u_form = ResidentUpdateForm(request.POST, instance=sel_resident)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Resident Detail Update Successful')
                return redirect('residents:resident_details', sel_resident.id)
            else:
                messages.error(request, 'Something Went Wrong, Unable to update Resident Details')
                messages.info(request, u_form.errors)
        else:
            u_form = ResidentUpdateForm(instance=sel_resident)
        context = {
            'form': u_form,
            'resident': sel_resident
        }

        return render(request, 'residents/dashboards/update_resident.html', context)


@login_required()
@admin_required()
def edit_property(request, resident_id, property_id):
    if resident_id is None:
        messages.error(request, 'No Resident Selected')
        return HttpResponseRedirect(reverse("residents:all_residents"))
    elif property_id is None:
        messages.error(request, 'No Property Selected')
        return HttpResponseRedirect(reverse("residents:resident_details"))
    else:
        try:
            sel_resident = Residents.objects.get(id=resident_id)
            sel_property = Properties.objects.get(id=property_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:all_residents"))

        if request.method == 'POST':
            u_form = EditPropertyForm(request.POST, instance=sel_property)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Property Edit Successful')
                return redirect('residents:resident_details', sel_resident.id)
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

        return render(request, 'residents/dashboards/update_properties.html', context)


class select_request(ListView):
    model = AccRequest
    queryset = AccRequest.objects.filter(status=0)
    template_name = 'residents/dashboards/get_request.html'
    context_object_name = 'requests'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(select_request, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')

        if query is None:
            all_requests = AccRequest.objects.all()
            context['searchq'] = all_requests
        else:
            context['searchq'] = query
        return context

    def get_queryset(self):
        queryset = super(select_request, self).get_queryset()
        query = self.request.GET.get('q')
        if query is None:
            return queryset
        else:
            query = query.replace(" ", "+")

            try:
                house = Houses.objects.get(housecode=query)
            except ObjectDoesNotExist:
                house = None

            queryset = AccRequest.objects.filter(
                Q(house__exact=house) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )

            return queryset


@login_required()
@admin_required()
def new_resident_request(request, house_id, request_id):
    if house_id is None:
        return HttpResponseRedirect(reverse("residents:select_request"))
    elif request_id is None:
        return HttpResponseRedirect(reverse("residents:select_request"))
    else:
        try:
            house = get_object_or_404(Houses, pk=house_id)
            # Check if there is a current active resident in the house and throw back a error
            if house.housestatus == 1:
                messages.info(request, "House is occupied, cannot add new resident")
                return HttpResponseRedirect(reverse("residents:select_request"))
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:select_request"))

        try:
            account_request = get_object_or_404(AccRequest, pk=request_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect(reverse("residents:select_request"))

    # Create Resident
    form = NewResidentForm(request.POST or None)
    req_first_name = account_request.first_name
    req_last_name = account_request.last_name
    req_email = account_request.email
    req_pword = account_request.password

    # Get form data
    if request.method == "POST":

        if form.is_valid():
            first_name = req_first_name
            last_name = req_last_name
            email = req_email
            p_word = req_pword
            status = form.cleaned_data.get("status")

            resident_code = 0

            # Generate Unique Resident Code
            # Randomly Choose Letters for adding to code
            def gencode():
                char1 = random.choice(string.ascii_uppercase)
                char2 = random.choice(string.ascii_lowercase)
                char3 = random.choice(string.ascii_letters)
                char4 = random.choice('1234567890')
                char5 = random.choice(string.ascii_uppercase)
                char6 = random.choice(string.ascii_lowercase)
                char7 = random.choice(string.ascii_letters)

                return f"rsd/{char1}{char2}{char3}-{char4}{char5}/{char6}{char7}"

            rsd = gencode()
            resident_code = rsd
            while Residents.objects.filter(resident_code=rsd):
                rsd = gencode()
                if not Residents.objects.filter(resident_code=gencode):
                    resident_code = gencode

            # Create User Account

            # Generate User Name
            def gen_name(firstname, lastname):
                gen = f"{lastname[:4]}{firstname[:3]}"
                user_name = gen.lower()

                while User.objects.filter(username=user_name):
                    similar_list = User.objects.filter(username__icontains=user_name).__len__()
                    inc_count = int(similar_list) + 1
                    user_name = f"{user_name}0{inc_count}"

                    if not User.objects.filter(username=user_name):
                        user_name = user_name

                return user_name
            usn = gen_name(first_name, last_name)
            users_name = usn

            nu = User.objects.create_user(username=users_name, email=email, password=p_word, first_name=first_name,
                                          last_name=last_name, user_type=3)
            nu.save()

            # Update Profile
            sel_user = User.objects.get(username=users_name)
            user_prof = Profile.objects.get(user=sel_user)

            user_prof.house = house
            user_prof.save()

            # Change Request Status
            account_request.status = 1
            account_request.save()

            rs = Residents.objects.create(user=sel_user, house=house, resident_code=resident_code,
                                          first_name=first_name,
                                          last_name=last_name, resident_email=email, occupancy_status=status)
            rs.save()
            if house.housestatus == 0:
                house.housestatus = 1
                house.save()
            messages.success(request, f'Resident {resident_code}-{first_name} {last_name} Added Successfully')

        else:
            messages.error(request, 'Error validating the form')
            messages.info(request, form.errors)
        return HttpResponseRedirect(reverse("residents:residents_dashboard"))

    context = {
        'house': house,
        'form': form,
        'account_request': account_request,
        'req_first_name': req_first_name,
        'req_last_name': req_last_name,
        'req_email': req_email
    }

    return render(request, 'residents/dashboards/new_resident_request.html', context)


@login_required()
@admin_required()
def cancel_account_request(request, pk):
    if pk is None:
        messages.error(request, 'No Request Selected')
        return HttpResponseRedirect(reverse("residents:select_request"))
    if request.method == 'POST':

        if request.POST.get('cancel') == 'True':
            try:
                sel_request = AccRequest.objects.get(pk=pk)
            except ObjectDoesNotExist:
                messages.error(request, 'Something Went Wrong')
                return HttpResponseRedirect(reverse('residents:select_request'))

            sel_request.status = 2
            sel_request.save()

            messages.success(request, 'Request Cancelled Successfully')
            return redirect('residents:select_request')

    messages.info(request, 'Something went wrong')
    return redirect('residents:select_request')
