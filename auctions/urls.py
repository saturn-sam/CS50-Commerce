from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add/listing", views.add_listing, name="add-listing"),
    path("closed/listing", views.closed_listing, name="closed-listing"),
    path("listing/<int:pk>", views.individual_listing, name="individual-listing"),
    path("show/watchlist", views.show_watchlist, name="show-watchlist"),
    path("winning/list", views.win_list, name="win-list"),
    path("my/listing", views.my_listing, name="my-listing"),
    path("category/list", views.category_list, name="category-list"),
    path("category/<int:pk>", views.cat_wise_listing, name="cat-wise-listing"),
]
