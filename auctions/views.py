from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Prefetch

from .models import User, Listing, Comment, Category, Watchlist, Bid

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.FloatField(label="Starting Bid")
    image_url = forms.CharField(label="Image URL")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), initial=0)

class CommentForm(forms.Form):
    comment = forms.CharField(label="Post a comment ")

class BidForm(forms.Form):
    bid = forms.FloatField(label="Place a bid")

def index(request):
    
    listings = Listing.objects.all()
    for listing in listings:
        bid = Bid.objects.filter(listing=listing.id).order_by('-bid').first()
        if bid:
            listing.bid = "${:,.2f}".format(bid.bid)
        else:
            listing.bid = "${:,.2f}".format(listing.starting_bid)

    return render(request, "auctions/index.html", {
        "listings": listings
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


def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    comments = Comment.objects.filter(listing_id=listing_id)
    current_bid = Bid.objects.filter(listing=listing).order_by('-bid').first()

    user = request.user
    w = None

    if not user.is_anonymous:
        try:
            w = Watchlist.objects.get(user=user, listing=listing)
        except Watchlist.DoesNotExist:
            w = None

    #determine if the user can close the listing or not
    can_close = False
    if listing.creator.id == user.id and listing.active:
        can_close = True

    #determine if the user is the winner of the listing
    is_winner = False
    if listing.active == False and listing.winner == user and not listing.creator == user:
        is_winner = True

    # determine bid
    if listing.active:
        if current_bid:
            bid = "Current bid: " + "${:,.2f}".format(current_bid.bid)
        else:
            bid = "Starting bid: " + "${:,.2f}".format(listing.starting_bid)
    else:
        if current_bid:
            bid = "Final bid: " + "${:,.2f}".format(current_bid.bid)
        else:
            bid = "Final bid: " + "${:,.2f}".format(listing.starting_bid)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "watchlist": w,
        "comment_form": CommentForm(),
        "current_bid": current_bid,
        "bid_form": BidForm(),
        "can_close": can_close,
        "is_winner": is_winner,
        "bid": bid
    })

def create_listing(request):
    user = request.user

    if user.is_anonymous:
        return HttpResponseRedirect('/login')

    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]

            l = Listing(title=title, description=description, starting_bid=starting_bid, image_url=image_url, category=category, creator=user)
            l.save()

            return HttpResponseRedirect('/listing/' + str(l.id))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    return render(request, "auctions/create.html", {
        "form":  NewListingForm()
    })

def close_listing(request, listing_id):
    user = request.user

    if user.is_anonymous:
        return HttpResponseRedirect('/login')

    #confirm listing belongs to logged user
    errors = []
    try:
        l = Listing.objects.get(creator=user, id=listing_id)
    except Listing.DoesNotExist:
        l = None
        errors.append("Unable to close listing")
    
    if l is None:
        return render(request, "auctions/error.html", {
            "errors": errors
        })

    # determine bid winner
    current_bid = Bid.objects.filter(listing=l).order_by('-bid').first()
    if current_bid:
        l.winner = current_bid.user 

    # update listing status
    l.active=False
    l.save()

    return HttpResponseRedirect('/listing/' + str(listing_id))

def comment(request):
    user = request.user

    if user.is_anonymous:
        return HttpResponseRedirect('/login')

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            listing_id = request.POST["listing_id"]
            comment = form.cleaned_data["comment"]
            l = Listing.objects.get(id=listing_id)
            c = Comment(comment=comment, listing=l, user=user)
            c.save()

    return HttpResponseRedirect('/listing/' + listing_id)

def watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(user=user.id).values_list('listing', flat=True)

    listings = Listing.objects.filter(id__in=watchlist)

    for listing in listings:
        bid = Bid.objects.filter(listing=listing.id).order_by('-bid').first()
        if bid:
            listing.bid = "${:,.2f}".format(bid.bid)
        else:
            listing.bid = "${:,.2f}".format(listing.starting_bid)

    return render(request, "auctions/watchlist.html", {
        "listings": listings 
    })

def watchlist_add(request, listing_id):
    user = request.user

    if user.is_anonymous:
        return HttpResponseRedirect('/login')

    listing = Listing.objects.get(id=listing_id)
    w = Watchlist.objects.get_or_create(user=user, listing=listing)
    
    return HttpResponseRedirect('/listing/' + str(listing_id))

def watchlist_remove(request, listing_id):
    user = request.user
    listing = Listing.objects.get(id=listing_id)
    w = Watchlist.objects.filter(listing=listing, user=user).delete()
    
    return HttpResponseRedirect('/listing/' + str(listing_id))

def place_bid(request):
    user = request.user

    if user.is_anonymous:
        return HttpResponseRedirect('/login')

    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            errors = []
            listing_id = request.POST["listing_id"]
            listing = Listing.objects.get(id=listing_id)
            bid = form.cleaned_data["bid"]
            
            current_bid = Bid.objects.filter(listing=listing).order_by('-bid').first()

            if current_bid:
                min_bid = current_bid.bid + 0.01
            else:
                min_bid = listing.starting_bid

            if bid >= min_bid:
                b = Bid(bid=bid, listing=listing, user=user)
                b.save()
            else:
                errors.append("Minimum bid amount is ${:,.2f}".format(min_bid))
                
                return render(request, "auctions/error.html", {
                    "listing": listing,
                    "errors": errors
                })

    return HttpResponseRedirect('/listing/' + str(listing_id))

def categories(request):
    
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all() 
    })

def category(request, category_id):
    listings = Listing.objects.filter(category=category_id)
    category = Category.objects.get(id=category_id)

    for listing in listings:
        bid = Bid.objects.filter(listing=listing.id).order_by('-bid').first()
        if bid:
            listing.bid = "${:,.2f}".format(bid.bid)
        else:
            listing.bid = "${:,.2f}".format(listing.starting_bid)
            
    return render(request, "auctions/category.html", {
        "category": category.name,
        "listings": listings
    })