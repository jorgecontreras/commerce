from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/close/<int:listing_id>", views.close_listing, name="close_listing"),
    path("listing/create", views.create_listing, name="create_listing"),
    path("listing/comment", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/add/<int:listing_id>", views.watchlist_add, name="watchlist_add"),
    path("watchlist/remove/<int:listing_id>", views.watchlist_remove, name="watchlist_remove"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("bid", views.place_bid, name="place_bid")

]
