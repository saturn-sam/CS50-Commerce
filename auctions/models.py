from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass



class Category(models.Model):
    category_name = models.CharField(max_length=50)
    added_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='category_added_by')
    added_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.category_name

class Listing(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='listing_creator_user')
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='listing_category')
    starting_bid = models.IntegerField()
    creation_date = models.DateTimeField(default=timezone.now)
    image = models.URLField(max_length = 300, blank=True, null=True)
    close_status = models.BooleanField(default=False)
    winner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='listing_winner', blank=True, null=True)

    def __str__(self):
        return f"Owner: {self.owner}, List Title: {self.title}, Close Status: {self.close_status}"

class Bid(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bid_user')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='listing_of_bid')
    bid_value = models.IntegerField()
    bid_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Listing: {self.listing}, Listing: {self.listing}, Bid Value: {self.bid_value}"

class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comment_user')
    comment = models.TextField()
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='comment_list')
    comment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"User: {self.user}, Listing: {self.listing}"

class Watchlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='watchlist_user')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='watchlist_listing', blank=True, null=True)

    def __str__(self):
        return f"User: {self.user}, Listing: {self.listing}"