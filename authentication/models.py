from djongo import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.crypto import get_random_string
import pandas as pd
import uuid


# Create your models here.
def check_mail(email):
    try:
        obj = User.objects.get(email=email)
        return True
    except:
        return False


def gen_username(email):
    username, domain = email.split("@")
    i = 1
    while 1:
        if i == 5:
            username = username
            break
        try:
            obj = User.objects.get(username=username)
            username = username + str(i)
            i += 1
        except:
            break
    return username


# Create your models here.


class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.username = str(username).lower()
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.is_admin = True
        user.is_staff = True
        user.role = "Student"
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    first_name = models.CharField(max_length=100, default="first_name")
    last_name = models.CharField(max_length=100, default="last_name")
    username = models.CharField(max_length=200, unique=True)
    role_choices = (
        ("Student", "Student"),
        ("Teacher", "Teacher")
    )
    role = models.CharField(max_length=50, choices=role_choices, default="Student")
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name' ]

    objects = UserAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class UserGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=100, blank=True)
    user = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class UserFromFile(models.Model):
    id = models.AutoField(primary_key=True)
    userdata = models.FileField(upload_to="userdata", max_length=1000)
    filename = models.CharField(max_length=100, default="output.csv", blank=True)
    group_name = models.CharField(max_length=50, null=True, blank=True)
    group = models.ManyToManyField(UserGroup,blank=True)

    def save(self, *args, **kwargs):
        super(UserFromFile, self).save(*args, **kwargs)
        user_group = UserGroup.objects.create(name=self.group_name)
        data = pd.read_csv(self.userdata)
        data.fillna("NA", inplace=True)
        for i in range(data.shape[0]):
            email = data.iloc[i]["Email"]
            if check_mail(email):
                data.loc[i, 'Username'] = "The email is already in use"
            else:
                username = gen_username(data.iloc[i]["Email"])
                first_name = data.iloc[i]["First Name"]
                try:
                    first_name,last_name = first_name.split()
                except:
                    last_name = data.iloc[i]["Last Name"]
                random_password = get_random_string(length=10)
                u = User.objects.create_user(email=email, username=username, first_name=first_name,
                last_name=last_name, password=random_password)
                u.save()
                user_group.user.add(u)
                data.loc[i, 'Username'] = username
                data.loc[i, 'Password'] = random_password
        self.filename = "media/users/" + "generated_user_details" + str(get_random_string(length=5)) + ".csv"
        data.to_csv(self.filename)