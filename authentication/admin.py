from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as GroupAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from authentication.models import User, UserFromFile, UserGroup


# Register your models here.


class UserCreationForm(forms.ModelForm):
    username = forms.CharField(label='Username')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'username', 'first_name', 'last_name','role', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'role')
    list_filter = ('role',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name','role')}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'is_verified', 'is_staff' )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name','role', 'password1', 'password2')}
         ),
    )
    search_fields = ('email', )
    ordering = ('-id', )
    filter_horizontal = ()

class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ('-id','name')

# class GroupMembershipAdmin(admin.ModelAdmin):
#     list_display = ('user', 'group')
#     ordering = ('id','group')

admin.site.register(User, UserAdmin)
# admin.site.unregister(Group)
admin.site.register(UserFromFile)
admin.site.register(UserGroup, UserGroupAdmin)
# admin.site.register(GroupMembership, GroupMembershipAdmin)