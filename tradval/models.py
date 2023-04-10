from django.contrib.auth.models import User
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created

# Create your models here.


class CompanyDetail(models.Model):
    company = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} '


class CompanyEvaluation(models.Model):
    company = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE)
    hs_code = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=50, null=True, blank=True)
    ref_date = models.CharField(max_length=20,null=True, blank=True)
    rate_1 = models.FloatField(default=0.00, null=True, blank=True)
    rate_2 = models.FloatField(default=0.00, null=True, blank=True)
    rate_3 = models.FloatField(default=0.00, null=True, blank=True)
    rate_4 = models.FloatField(default=0.00, null=True, blank=True)
    rate_5 = models.FloatField(default=0.00, null=True, blank=True)
    total = models.FloatField(default=0.00, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.company.name} '


class CompanyReviews(models.Model):
    company = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(CompanyEvaluation, on_delete=models.CASCADE)
    review = models.CharField(max_length=160, null=True, blank=True)
    have_review = models.BooleanField(default=False, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.company.name} '

class EvaluationRequest(models.Model):
    sender = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE,related_name='sender')
    receiver = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE,related_name='receiver')
    hs_code = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=50, null=True, blank=True)
    ref_date = models.CharField(max_length=20,null=True, blank=True)
    notif = models.BooleanField(default=False, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.name} '

class CompanyClaims(models.Model):
    claimer = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE,related_name='claimer', null=True, blank=True)
    claimest = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE,related_name='claimest', null=True, blank=True)
    evaluation = models.ForeignKey(CompanyEvaluation, on_delete=models.CASCADE,null=True, blank=True)
    reviews = models.ForeignKey(CompanyReviews, on_delete=models.CASCADE,null=True, blank=True)
    action = models.CharField(max_length=50, null=True, blank=True)
    ref_date = models.CharField(max_length=20,null=True, blank=True)
    notif = models.BooleanField(default=False, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.claimer.name} '

class CompanyActivity(models.Model):
    company = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(CompanyEvaluation, on_delete=models.CASCADE,null=True, blank=True)
    reviews = models.ForeignKey(CompanyReviews, on_delete=models.CASCADE,null=True, blank=True)
    request = models.ForeignKey(EvaluationRequest, on_delete=models.CASCADE,null=True, blank=True)
    claim = models.ForeignKey(CompanyClaims, on_delete=models.CASCADE,null=True, blank=True)
    ip = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.company.name} '
class CompanyLookUp(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    ip = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} '

class UserByUser(models.Model):
    company = models.OneToOneField(User, on_delete=models.CASCADE)
    create_by = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE,null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    pwd = models.CharField(max_length=10, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

class ContactSupport(models.Model):
    company = models.ForeignKey(CompanyDetail, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,null=True,blank=True)
    message = models.CharField(max_length=200,null=True,blank=True)
    answer = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


def userByUserInvitation(sender, instance, *args, **kwargs):
    context = {
        'Company': instance.company.last_name,
        'invited': instance.create_by.name,
        'email': instance.email,
        'pwd': instance.pwd
    }
    email_html_message = render_to_string('email/invitation.html', context)
    email_plaintext_message = render_to_string('email/invitation.txt', context)
    msg = EmailMultiAlternatives(
        # title:
        "Customer Evaluation Received ",
        # message:
        email_plaintext_message,
        # from:
        "noreply@tradval.com",
        # to:
        [instance.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
post_save.connect(userByUserInvitation,sender=UserByUser)

def userRequestInvitation(sender, instance, *args, **kwargs):
    context = {
        'Company': instance.sender.name,
        'invited': instance.receiver.name,

    }
    email_html_message = render_to_string('email/request.html', context)
    email_plaintext_message = render_to_string('email/request.txt', context)
    msg = EmailMultiAlternatives(
        # title:
        "Evaluation Request ",
        # message:
        email_plaintext_message,
        # from:
        "noreply@tradval.com",
        # to:
        [instance.receiver.company.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
post_save.connect(userRequestInvitation,sender=EvaluationRequest)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "http://127.0.0.1:5500/pwdconfirm.html?token={}".format(
            reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="TradVal"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@tradval.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()