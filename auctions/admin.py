from django.contrib import admin

# Register your models here.
from .models import Listing, Category, Comment, Watchlist, Bid

admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Watchlist)
admin.site.register(Bid)
