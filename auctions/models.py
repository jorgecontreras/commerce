from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    starting_bid = models.FloatField()
    image_url = models.CharField(max_length=256, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    creator= models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    comment = models.CharField(max_length=256)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comment}"

class Bid(models.Model):
    """store the many-to-many relationship between listing and bid"""
    bid = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bid")

    def __str__(self):
        return f"user:{self.user.id}, listing: {self.listing.title}, bid: {self.bid}"

class Watchlist(models.Model):
    """Many-to-many relationship between User and watched listings"""
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing")

    def __str__(self):
        return f"user:{self.user.id}, listing: {self.listing.title}"

    class Meta:
        unique_together = ('user', 'listing',)