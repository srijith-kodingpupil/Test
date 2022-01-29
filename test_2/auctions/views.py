from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Bids, Comments, Watchlist


def index(request):
    return render(request, "auctions/index.html",{
        "listings" : Listing.objects.all().filter(active = True),
        "bids" : Bids.objects.all(),
        "header": "Active Listings.",
        "in_listings" : Listing.objects.all().filter(active = False),
        "in_bids" : Bids.objects.all(),
        "in_header": "Inactive Listings."
    })



def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def categories(request):
    category_list = []
    categories_list = Listing.objects.all()
    for i in categories_list:
        if i.category:
            if i.category not in category_list:
                category_list.append(i.category)
    return render(request, "auctions/categories.html",{
        "categories": category_list
        
    })

def listing(request, listing_id):
    li = Listing.objects.filter(id = listing_id).first()
    bids = Bids.objects.filter(listing = li)
    comm = Comments.objects.filter(listing = li)
    highest_bid = li.base_bid
    if bids is not None:
        for bid in bids:
            if bid.price > highest_bid:
                highest_bid = bid.price
                
    if request.method == 'POST':
        price = request.POST.get('bid_price', None)
        user = request.user
        listing = Listing.objects.filter(id = listing_id).first()
        comment = request.POST.get('comment', None)

        try:
            price = int(price)
        except:
            price = None
        
        if comment is not None:
            comm = Comments.objects.create(contents = comment, user = user, listing = listing)
            comm.save()
            return HttpResponseRedirect(reverse('listing', args = [listing_id]))
        
        if price is not None:
            if int(price) < highest_bid:
                return HttpResponseRedirect(reverse('listing', args = [listing_id]))
            bids = Bids.objects.create(price = int(price), user = user, listing = listing)
            bids.save()
            bs = Bids.objects.filter(listing = listing).exclude(price = price)
            bs.delete() 
            return HttpResponseRedirect(reverse('listing', args = [listing_id]))
        
        if price is None and comment is None:
            return render(request, "auctions/listing.html", {
                "message": "Must Login/Register to bid or comment",
                "listing": li,
                "highest_bid": highest_bid,
                "min_bid": (highest_bid + 1),
                "comments": comm
            })
        
    return render(request, "auctions/listing.html", {
        "listing": li,
        "highest_bid": highest_bid,
        "min_bid": (highest_bid + 1),
        "comments": comm
    })


def list_categories(request, category):
    li = Listing.objects.all().filter(category = category)
    return render(request, "auctions/list_categories.html", {
        "listings": li
    })

def create(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        base_bid = request.POST['starting_bid']
        img_url = request.POST['img_url']
        category = request.POST['category']
        user = request.user
        li = Listing.objects.create(title = title,
                              category = category,
                              base_bid = base_bid,
                              description = description,
                              img_url = img_url,
                              user = user)
        li.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html",{
        "listings" : Listing.objects.all().filter(active = True),
    })

def watchlist(request):
    user = request.user
    wl = Watchlist.objects.filter(user = user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": wl,
        "listings" : Listing.objects.all().filter(active = True),
    })

def toggle_watchlist(request, listing_id):
    user = request.user
    li = Listing.objects.filter(id = listing_id).first()
    wl = Watchlist.objects.filter(user = user, listing = li).first()
    if wl is None:
        w_l = Watchlist.objects.create(user = user, listing = li)
        w_l.save()
        return HttpResponseRedirect(reverse("watchlist"))
    wl.delete()
    return HttpResponseRedirect(reverse("watchlist"))

def close(request, listing_id):
    li = Listing.objects.filter(id = listing_id).first()
    bids = Bids.objects.filter(listing = li).first()
    if li.user == request.user and not bids is None:
        li.active = False
        li.winner = bids.user
        li.save()
        return HttpResponseRedirect(reverse('index'))
    elif li.user == request.user and bids is None:
        li.active = False
        li.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/error.html", {
            "error": "You cannot close other's listings."
        })