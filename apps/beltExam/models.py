from __future__ import unicode_literals
from django.db import models
import datetime
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX =re.compile('^[A-z]+$')

class UserManager(models.Manager):
    def register(self, postData):
        errors = []
        # Check whether email exists in db
        if User.objects.filter(email=postData['email']):
            errors.append('Email is already registered')
        # Validate first name
        if len(postData['first_name']) < 2:
            errors.append('First name must be at least 2 characters')
        elif not NAME_REGEX.match(postData['first_name']):
            errors.append('First name must only contain alphabet')
        # Validate last name
        if len(postData['last_name']) < 2:
            errors.append('Last name must be at least 2 characters')
        elif not NAME_REGEX.match(postData['last_name']):
            errors.append('Last name must only contain alphabet')
        # Validate email
        if len(postData['email']) < 1:
            errors.append('Email cannot be blank')
        elif not EMAIL_REGEX.match(postData['email']):
            errors.append('Invalid email format')
        # Validate password
        if len(postData['password']) < 8:
            errors.append('Password must be at least 8 characters')
        # Validate confirm password
        elif postData['password'] != postData['confirm']:
            errors.append('Passwords do not match')
        # Validate date
        if postData['date'] == '':
            errors.append('Hire date cannot be blank')
        elif len(postData['date']) > 10:
            errors.append('Hire date must be valid date')
        else:
            current = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            cYear = int(current[:4])
            cMonth = int(current[5:7])
            cDay = int(current[8:])
            postData['date'] = str(postData['date'])
            year = int(postData['date'][:4])
            month = int(postData['date'][5:7])
            day = int(postData['date'][8:])
            if (year > cYear) or (year == cYear and month > cMonth) or (year == cYear and month == cMonth and day > cDay):
                errors.append('Hire date must be in the past')

        # if no errors
        if len(errors) == 0:
            # Generate new salt
            salt = bcrypt.gensalt()
            # Form data must be encoded before hashing
            password = postData['password'].encode()
            # Hash pw with password and salt
            hashed_pw = bcrypt.hashpw(password, salt)
            # add to database
            User.objects.create(first_name=postData['first_name'], last_name=postData['last_name'], email=postData['email'], password=hashed_pw, date_hired=postData['date'])

        return errors

    def login(self, postData):
        errors = []
        # if email is found in db
        if User.objects.filter(email=postData['email']):
            form_pw = postData['password'].encode()
            db_pw = User.objects.get(email=postData['email']).password.encode()
            print db_pw
            # if hashed passwords do not match
            if not bcrypt.checkpw(form_pw, db_pw):
                errors.append('Incorrect password')
        # else if email is not found in db
        else:
            errors.append('Email has not been registered')
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    date_hired = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __unicode__(self):
        return str(self.id) + ' - ' + self.first_name + self.last_name + ' - ' + self.email + ' - ' + self.password + ' - ' + str(self.date_hired)

class ProductManager(models.Manager):
    def check_product(self, postData):
        errors = []
        if len(postData['item']) < 4:
            errors.append('Field must be more than 3 characters')
            return errors
        # Add item to Product table
        Product.objects.create(item=postData['item'], user_id=postData['userID'])
        # Retrieve latest product id from Product table
        product = Product.objects.latest('id')
        # Add to logged user's wishlist
        Wishlist.objects.create(user_id=postData['userID'], product_id=product.id)
        return errors

class Product(models.Model):
    item = models.CharField(max_length=45)
    user = models.ForeignKey(User, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ProductManager()
    def __unicode__(self):
        return str(self.id) + ' - ' + self.item + ' - ' + self.user.first_name

class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishes')
    product = models.ForeignKey(Product, related_name='wishes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.user.first_name) + ' - ' + str(self.product.item)
