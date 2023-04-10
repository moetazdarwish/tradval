from django.contrib.auth.forms import UserCreationForm,forms
from django.contrib.auth.models import User

class CreateUser(UserCreationForm):

    class Meta:
        model = User
        fields = [ 'email','username','first_name','last_name','password1','password2']

class CreateUserbyUser(UserCreationForm):

    class Meta:
        model = User
        fields = [ 'email','username','first_name','last_name']