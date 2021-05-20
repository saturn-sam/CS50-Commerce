from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import User, Listing, Watchlist, Comment, Bid, Category
from .forms import ListingAddForm

# def index(request):
#     return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
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

def index(request):
    listing = Listing.objects.filter(close_status=False).order_by('-id')

    for i in listing:
        if Bid.objects.filter(listing=i.id).order_by('-id'):
            bid = Bid.objects.filter(listing=i.id).order_by('-id')[0]
            current_bid_value = bid.bid_value
            i.current_price = current_bid_value
           
        else:
            i.current_price = i.starting_bid
           

    if request.user.id is None:
        context = {
            'listings': listing,
        }
        return render(request, "auctions/index.html", context)
    # watchlist = Watchlist.objects.all()
    # watchlist = Watchlist.objects.filter(user=request.user)
    watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
    context = {
        'listings': listing,
        'watchlist_item_count': watchlist_item_count,
        # 'watchlist': watchlist,
    }
    return render(request, "auctions/index.html", context)

@login_required    
def closed_listing(request):
    listing = Listing.objects.filter(close_status=True).order_by('-id')
    for i in listing:
        if Bid.objects.filter(listing=i.id).order_by('-id'):
            bid = Bid.objects.filter(listing=i.id).order_by('-id')[0]
            current_bid_value = bid.bid_value
            i.current_price = current_bid_value
            
        else:
            i.current_price = i.starting_bid
               
    watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
    context = {
        'listings': listing,
        'watchlist_item_count': watchlist_item_count,
    }
    return render(request, "auctions/closed_list.html", context)

@login_required
def add_listing(request):
    # watchlist = Watchlist.objects.filter(user=request.user)
    watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
    
    if request.method == 'POST':
        form_listing = ListingAddForm(request.POST)

        if form_listing.is_valid():
            # form_listing.save()
            title = form_listing.cleaned_data['title']
            description = form_listing.cleaned_data['description']
            category = form_listing.cleaned_data['category']
            starting_bid = form_listing.cleaned_data['starting_bid']
            image = form_listing.cleaned_data['image']

            Listing.objects.create(
                owner=request.user,
                title=title, 
                description=description, 
                starting_bid=starting_bid,
                category=category,
                image=image,
            )
            
            return redirect('index')        

    else:

        context = {
            'form': ListingAddForm(),
            'watchlist_item_count': watchlist_item_count,
        }

        return render(request, "auctions/add_listing.html", context)

def individual_listing(request, pk):
    bid = Bid.objects.filter(listing=pk).order_by('-id')
    listing_item = Listing.objects.get(id=pk)
    user_watchlist_status = None
    watchlist_item_count = None
    bid_number = 0
    message = None
    comment_message = None
    if not request.user.id == None:
        watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
        user_watchlist_status = Watchlist.objects.filter(Q(user=request.user) & Q(listing=pk))

    if bid:
        last_bid = Bid.objects.filter(listing=pk).order_by('-id')[0]
        last_bid_value = last_bid.bid_value
        bid_number = bid.count()
    else:
        last_bid_value = Listing.objects.get(id=pk).starting_bid

    if request.method == 'POST':
        if 'bid' in request.POST:
            bid_amount = request.POST["bid-amount"]
            if request.user != listing_item.owner:
                if bid_amount:
                    if int(last_bid_value) >= int(bid_amount):
                        message = "Bid value must be greater than current bid."
                    else:
                        Bid.objects.create(
                            user = request.user,
                            listing = listing_item,
                            bid_value = bid_amount
                        )
                        bid_number+=1
                        last_bid_value = bid_amount
                else:
                    message = "You must add a value in bid amount greater than current bid."
            else:
                message = "You cant bid on your listing."


        elif 'addtowatchlist' in request.POST:
            if not user_watchlist_status:
                Watchlist.objects.create(
                    user=request.user,
                    listing=listing_item
                )
                user_watchlist_status = Watchlist.objects.filter(Q(user=request.user) & Q(listing=pk))
                watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
            else:
                Watchlist.objects.filter(Q(user=request.user) & Q(listing=pk)).delete()
                user_watchlist_status = Watchlist.objects.filter(Q(user=request.user) & Q(listing=pk))
                watchlist_item_count = Watchlist.objects.filter(user=request.user).count()


        elif 'commentbtn' in request.POST:
            comment = request.POST["comment"]
            if comment:
                Comment.objects.create(
                    user = request.user,
                    comment = comment,
                    listing = listing_item
                )
            else:
                message = "You must add something in textbox."


        elif 'deletebid' in request.POST:
            Listing.objects.get(id=pk).delete()
            return redirect('index')


        elif 'closebid' in request.POST:
            if Bid.objects.filter(listing=pk):
                # last_bid = Bid.objects.filter(listing=pk).order_by('-id')[0]
                listing_close = Listing.objects.get(id=pk)
                listing_close.close_status = True
                listing_close.winner = last_bid.user
                listing_close.save()
            else:
                message = "No bid on this auction! You can delete the bid instead of close"

    product_watchlisted = Watchlist.objects.filter(listing=pk).count()
    comment = Comment.objects.filter(listing=pk).order_by('-id')    
    
    context = {
        'listing_item': listing_item,
        'watchlist_item_count':watchlist_item_count,
        'comments':comment,
        'product_watchlisted':product_watchlisted,
        'last_bid_value':last_bid_value,
        'message':message,
        'bid_number':bid_number,
        'user_watchlist_status':user_watchlist_status
    }
    return render(request, 'auctions/list_item_show.html', context) 

@login_required
def show_watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    # listing = Listing.objects.filter(id=watchlist.listing.id)
    # watchlist_item_count = None
    watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
    context = {
        'watchlists': watchlist,
        'watchlist_item_count': watchlist_item_count,
        # 'listings': listing
    }
    return render(request, "auctions/watchlist.html", context)

@login_required
def win_list(request):
    my_winning_list = Listing.objects.filter(winner=request.user)
    watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
    context = {
        'my_winning_lists': my_winning_list,
        'watchlist_item_count': watchlist_item_count,
        # 'listings': listing
    }
    return render(request, "auctions/my_winning_list.html", context)

@login_required
def my_listing(request):
    my_list = Listing.objects.filter(owner=request.user)
    watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
    context = {
        'my_lists': my_list,
        'watchlist_item_count': watchlist_item_count,
    }
    return render(request, "auctions/my_list.html", context)

def cat_wise_listing(request, pk):
    cat_listing = Listing.objects.filter(category=pk)
    watchlist_item_count = None
    if not request.user.id is None:
        watchlist_item_count = Watchlist.objects.filter(user=request.user).count()
    context = {
        'cat_listings': cat_listing,
        'watchlist_item_count': watchlist_item_count,
    }
    return render(request, "auctions/cat_listing.html", context)    

def category_list(request):
    category = Category.objects.all()
    watchlist_item_count = None
    if not request.user.id is None:
        watchlist_item_count = Watchlist.objects.filter(user=request.user).count()

    context = {
        'category': category,
        'watchlist_item_count': watchlist_item_count,
    }    
    return render(request, "auctions/category.html", context)