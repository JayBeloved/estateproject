from django.contrib.auth.decorators import login_required
from ..core.decorators import admin_required
from django.shortcuts import render

from django.views.generic import ListView

from django.contrib import messages

from django.http.response import HttpResponseRedirect

from django.urls import reverse

from .models import CommunityType, Community, HouseType, Houses

from .forms import HousetypeCreationForm, CommunityTypeCreationForm, CommunityCreationForm, HouseApprovalForm

import random
import string


# Create your views here.
@login_required()
@admin_required()
def housetype_dashboard(request):
    # Get data for Counters

    # Query All Data
    all_commtype = CommunityType.objects.all()
    all_communities = Community.objects.all()
    all_housetype = HouseType.objects.all()
    all_houses = Houses.objects.all()
    house_count = all_houses.count()
    commtype_count = all_commtype.count()
    communities_count = all_communities.count()
    housetype_count = all_housetype.count()

    # Query numbered HouseType
    housetypes = HouseType.objects.order_by('id')[:3]

    # Create New House Type
    form = HousetypeCreationForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            htype = form.cleaned_data.get("htype")
            is_block = form.cleaned_data.get("is_block")
            block_count = form.cleaned_data.get("block_count")
            is_flat = form.cleaned_data.get("is_flat")
            flat_count = form.cleaned_data.get("flat_count")

            if HouseType.objects.filter(htype=htype).exists():
                messages.error(request, f'House Type - {htype} Already Exists.')
            else:
                ht = HouseType.objects.create(htype=htype, is_block=is_block, block_count=block_count, is_flat=is_flat,
                                          flat_count=flat_count)
                ht.save()
                housetypes = HouseType.objects.order_by('id')
                messages.success(request, f'House Type - {htype} Added Successfuly')

        else:
            messages.error(request, 'Error validating the form')

        return HttpResponseRedirect(reverse("housetype:housetype_dashboard"))

    context = {
        'housetype_count': housetype_count,
        'commtype_count': commtype_count,
        'communities_count': communities_count,
        'house_count': house_count,
        'all_housetypes': all_housetype,
        'housetypes': housetypes,

        'form': form
    }
    return render(request, "structure/dashboards/housetype.html", context)


class HouseTypeListView(ListView):
    model = HouseType
    template_name = "structure/all/all_housetype.html"
    context_object_name = "housetypes"
    ordering = ['-id']
    paginate_by = 6


@login_required()
@admin_required()
def commtype_dashboard(request):
    # Get data for Counters

    # Query All Data
    all_commtype = CommunityType.objects.all()
    all_communities = Community.objects.all()
    all_housetype = HouseType.objects.all()
    all_houses = Houses.objects.all()
    house_count = all_houses.count()
    commtype_count = all_commtype.count()
    communities_count = all_communities.count()
    housetype_count = all_housetype.count()

    # Query numbered Community Type
    commtypes = CommunityType.objects.order_by('-id')[:5]

    # Create New Community Type
    form = CommunityTypeCreationForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            housetype = form.cleaned_data.get("housetype")
            commtype = form.cleaned_data.get("commtype")
            description = form.cleaned_data.get("description")

            if CommunityType.objects.filter(commtype=commtype).exists():
                messages.error(request, f'Community Type - {commtype} Already Exists.')
            elif CommunityType.objects.filter(housetype=housetype).exists():
                messages.error(request, f'Cannot attach more than one community to a house type.')
            else:
                ht = CommunityType.objects.create(housetype=housetype, commtype=commtype, description=description)
                ht.save()
                commtypes = CommunityType.objects.order_by('-id')[:5]
                messages.success(request, f'Community Type - {commtype} Added Successfully.')
        else:
            messages.error(request, 'Error validating the form')

        return HttpResponseRedirect(reverse("commtype:commtype_dashboard"))

    context = {
        'housetype_count': housetype_count,
        'commtype_count': commtype_count,
        'communities_count': communities_count,
        'house_count': house_count,
        'all_housetypes': all_housetype,
        'commtypes': commtypes,

        'form': form
    }
    return render(request, "structure/dashboards/commtype.html", context)


class CommunityTypeListView(ListView):
    model = CommunityType
    template_name = "structure/all/all_commtype.html"
    context_object_name = "commtypes"
    ordering = ['-id']
    paginate_by = 6


@login_required()
@admin_required()
def communities_dashboard(request):
    # Get data for Counters

    # Query All Data
    all_commtype = CommunityType.objects.all()
    all_communities = Community.objects.all()
    all_housetype = HouseType.objects.all()
    all_houses = Houses.objects.all()
    house_count = all_houses.count()
    commtype_count = all_commtype.count()
    communities_count = all_communities.count()
    housetype_count = all_housetype.count()

    # Query numbered Communities
    communities = Community.objects.order_by('-id')[:5]

    # Create New Community
    form = CommunityCreationForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            communitytype = form.cleaned_data.get("communitytype")
            commnum = form.cleaned_data.get("commnum")
            commcode = f"{communitytype}{commnum}"
            # Generate Community Code

            if Community.objects.filter(commcode=commcode).exists():
                messages.error(request, f'Community - {commcode} Already Exists.')
            else:
                ht = Community.objects.create(communitytype=communitytype, commnum=commnum, commcode=commcode)
                ht.save()
                communities_count = all_communities.count()
                messages.success(request, f'Community - {commcode} Added Successfuly')
        else:
            messages.error(request, 'Error Validating The Form')

        return HttpResponseRedirect(reverse("communities:communities_dashboard"))

    context = {
        'housetype_count': housetype_count,
        'commtype_count': commtype_count,
        'communities_count': communities_count,
        'house_count': house_count,
        'all_housetypes': all_housetype,
        'communities': communities,
        'form': form
    }
    return render(request, "structure/dashboards/communities.html", context)


class CommunityListView(ListView):
    model = Community
    template_name = "structure/all/all_communities.html"
    context_object_name = "communities"
    ordering = ['-id']
    paginate_by = 6


@login_required()
@admin_required()
def houses_dashboard(request):
    # Get data for Counters

    # Query All Data
    all_commtype = CommunityType.objects.all()
    all_communities = Community.objects.all()
    all_housetype = HouseType.objects.all()
    all_houses = Houses.objects.all()
    house_count = all_houses.count()
    commtype_count = all_commtype.count()
    communities_count = all_communities.count()
    housetype_count = all_housetype.count()

    # Query numbered Community Type
    houses = Houses.objects.order_by('-id')[:5]

    # Create New Community Type
    form = HouseApprovalForm(request.POST or None)

    if request.method == "POST":

        approval = request.POST['approval']

        if approval:
            total_houses = 0
            for community in all_communities:
                # Generator
                if community.communitytype.housetype.is_block:
                    if community.communitytype.housetype.is_flat:
                        # With Flats
                        # get number of blocks
                        block_count = community.communitytype.housetype.block_count
                        b_num = 0
                        for block in range(1, block_count + 1):
                            b_num += 1
                            b_code = f"BL{b_num}"
                            # get number of flats
                            flat_count = community.communitytype.housetype.flat_count
                            f_num = 0
                            f_code = None
                            for flat in range(1, flat_count + 1):
                                f_num += 1
                                f_code = f"FT{f_num}"
                                h_code = f"{community.commcode}/{b_code}/{f_code}"
                                h_status = 0

                                if Houses.objects.filter(housecode=h_code).exists():
                                    pass
                                else:
                                    house = Houses.objects.create(community=community, housecode=h_code,
                                                                  housestatus=h_status)
                                    house.save()
                                    total_houses += 1
                    else:
                        # Without Flats
                        # get number of blocks
                        block_count = community.communitytype.housetype.block_count
                        b_num = 0
                        for block in range(1, block_count + 1):
                            b_num += 1
                            b_code = f"BL{b_num}"
                            # Randomly Choose Letters for adding to code
                            char1 = random.choice(string.ascii_uppercase)
                            char2 = random.choice(string.ascii_lowercase)
                            char3 = random.choice(string.ascii_letters)
                            char4 = random.choice('123456789')
                            ##########################
                            h_code = f"{community.commcode}/{b_code}/{char1}{char2}{char3}{char4}"
                            h_status = 0
                            if Houses.objects.filter(housecode__contains=f'{community.commcode}/{b_code}'):
                                pass
                            else:
                                house = Houses.objects.create(community=community, housecode=h_code,
                                                              housestatus=h_status)
                                house.save()
                                total_houses += 1
            messages.success(request, f"A Total of {total_houses} Houses added successfully")
        else:
            pass
        houses = Houses.objects.order_by('id')[:5]

        return HttpResponseRedirect(reverse("houses:houses_dashboard"))

    context = {
        'housetype_count': housetype_count,
        'commtype_count': commtype_count,
        'communities_count': communities_count,
        'house_count': house_count,
        'all_housetypes': all_housetype,
        'houses': houses,

        'form': form,

    }

    return render(request, "structure/dashboards/houses.html", context)


class HouseListView(ListView):
    model = Houses
    template_name = "structure/all/all_houses.html"
    context_object_name = "houses"
    ordering = ['-id']
    paginate_by = 6
