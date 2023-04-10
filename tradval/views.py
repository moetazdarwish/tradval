import json
import datetime
from unicodedata import decimal
import uuid
import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from rest_framework.views import APIView

from tradval.form import CreateUser, CreateUserbyUser
from tradval.models import *
from tradval.tradvalseriaziler import *
from django.db.models import Avg

from tradval.utils import BurstRateThrottle


def get_IP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_User_IP(ip):
    url = 'http://ip-api.com/json/' + ip
    response = requests.get(url)
    data = response.json()
    return data


@api_view(['POST'])
def loginUser(request):
    username = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        get_user = User.objects.get(username=user)
        token, create = Token.objects.get_or_create(user=get_user)
        try:
            name = CompanyDetail.objects.get(company=get_user)
            key = token.key
            data = {"key": key,
                    "company": name.name,
                    }
            json_stuff = LogininSerializer(data).data
            return Response(json_stuff)
        except:
            return JsonResponse('Wrong Password ', safe=False)
    else:
        return JsonResponse('Wrong Password or Email', safe=False)


@api_view(['POST'])
def createUser(request):
    company = request.POST.get('company')
    manager = request.POST.get('manager')
    email = request.POST.get('email')
    password = request.POST.get('password')
    country = request.POST.get('country')
    type = request.POST.get('type')
    phone = request.POST.get('phone')

    data = {
        'first_name': manager,
        'last_name': company,
        'email': email,
        'username': email,
        'password1': password,
        'password2': password,
    }
    form = CreateUser(data)

    if form.is_valid():
        user = form.save()
        name = CompanyDetail.objects.create(company=user, name=company, country=country,
                                            tel=phone, type=type)
        token, create = Token.objects.get_or_create(user=user)
        key = token.key
        data = {"key": key,
                "company": name.name,
                }
        json_stuff = LogininSerializer(data).data
        return Response(json_stuff)
    else:
        return Response(form.errors)

class companySearch(APIView):
    throttle_scope = 'public'
    def post(self, request, format=None):

        company = request.POST.get('company')
        country = request.POST.get('country')

        ip = get_IP(request)
        # user_ip = get_User_IP('154.180.243.203')
        # print(user_ip['country'])
        CompanyLookUp.objects.create(name=company, country=country, ip=ip)
        if len(company) >= 3 and len(country) >= 3:
            instance = CompanyDetail.objects.filter(Q(name__contains=company) & Q(country__contains=country))
            data = {}
            if instance:
                data = CompanySerializer(instance, many=True).data

                return Response(data)
            else:
                data = {
                    'error': 'error',
                    'msg': 'No record'
                }
                return Response(data)
        else:
            data = {
                'error': 'error',
                'msg': 'Wrong Company Name'
            }
            return Response(data)

class userCompanySearch(APIView):
    throttle_scope = 'subscriber'
    def post(self, request, format=None):

        company = request.POST.get('company')
        country = request.POST.get('country')

        ip = get_IP(request)
        # user_ip = get_User_IP('154.180.243.203')
        # print(user_ip['country'])
        CompanyLookUp.objects.create(name=company, country=country, ip=ip)
        if len(company) >= 3 and len(country) >= 3:
            instance = CompanyDetail.objects.filter(Q(name__contains=company) & Q(country__contains=country))
            data = {}
            if instance:
                data = CompanySerializer(instance, many=True).data

                return Response(data)
            else:
                data = {
                    'error': 'error',
                    'msg': 'No record'
                }
                return Response(data)
        else:
            data = {
                'error': 'error',
                'msg': 'Wrong Company Name'
            }
            return Response(data)


@api_view(['POST'])
def evaluationResults(request):
    comp_id = request.POST.get('id')
    get_comp = CompanyDetail.objects.get(id=comp_id)
    get_count = CompanyEvaluation.objects.filter(company=get_comp).count()
    get_action = CompanyClaims.objects.filter(claimest=get_comp, action__isnull=False).count()
    get_reviews = CompanyReviews.objects.filter(company=get_comp)
    count_reviews = CompanyReviews.objects.filter(company=get_comp).count()
    get_avr = CompanyEvaluation.objects.filter(company=get_comp).aggregate(priceAvg=Avg('total'))['priceAvg']
    get_post = CompanyEvaluation.objects.filter(company=get_comp, total__gte=50).count()
    get_neg = CompanyEvaluation.objects.filter(company=get_comp, total__lt=50).count()
    get_cust = CompanyActivity.objects.filter(evaluation__company=get_comp)
    cust = 0
    prev = 0
    for i in get_cust:
        if prev != i.company.id:
            cust = cust + 1
        prev = i.company.id
    reviews = []
    for i in get_reviews:
        data = {
            "review": i.review,
            "date": i.date.strftime("%d/%m/%Y")
        }
        reviews.append(data)

    send_data = {
        'reviews': reviews,
        'count': get_count,
        'action': get_action,
        'average': round(get_avr, 2),
        'positive': round((get_post / get_count) * 100, 2),
        'negative': round((get_neg / get_count) * 100, 2),
        'customers': cust,
        'creview': count_reviews,

    }

    return JsonResponse(send_data)


@api_view(['POST'])
def evaluationPReviews(request):
    comp_id = request.POST.get('id')
    get_comp = CompanyDetail.objects.get(id=comp_id)
    get_reviews = CompanyReviews.objects.filter(company=get_comp)
    reviews = []
    for i in get_reviews:
        try:
            get_claims = CompanyClaims.objects.get(reviews=i.id)
            data = {
                'review': i.review,
                'date': i.date.strftime("%d/%m/%Y"),
                'action': get_claims.action
            }
            reviews.append(data)
        except:
            data = {
                'review': i.review,
                'date': i.date.strftime("%d/%m/%Y"),
                'action': "No Action Taken"
            }
            reviews.append(data)
    send_data = {
        'reviews': reviews
    }

    return Response(send_data)


@api_view(['POST'])
def createUserByUser(request):
    company = request.POST.get('company')
    manager = request.POST.get('manager')
    email = request.POST.get('email')
    country = request.POST.get('country')
    type = request.POST.get('type')
    phone = request.POST.get('phone')
    creator = CompanyDetail.objects.get(company=request.user)
    c_pwd = uuid.uuid4().hex
    pwd = c_pwd[:8]
    data = {
        'first_name': manager,
        'last_name': company,
        'email': email,
        'username': email,
        'password1': pwd,
        'password2': pwd,
    }
    form = CreateUser(data)

    if form.is_valid():
        user = form.save()
        name = CompanyDetail.objects.create(company=user, name=company, country=country,
                                            tel=phone, type=type)
        UserByUser.objects.create(company=user, create_by=creator, email=email, pwd=pwd)
        data = {"id": name.id,
                "company": name.name,
                }
        json_stuff = CreatByUserSerializer(data).data
        return Response(json_stuff)
    else:
        return JsonResponse(form.errors)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def companyAddEvaluation(request):
    comp_id = request.POST.get('id')
    quality = request.POST.get('quality')
    document = request.POST.get('document')
    response = request.POST.get('response')
    packing = request.POST.get('packing')
    recommend = request.POST.get('recommend')
    total = int(request.POST.get('score'))
    review = request.POST.get('review')
    hs_code = request.POST.get('hs_code')
    description = request.POST.get('description')
    ref = request.POST.get('ref')
    ref_date = request.POST.get('ref_date')
    ip = get_IP(request)
    evaluator = CompanyDetail.objects.get(company=request.user)
    evaluate = CompanyDetail.objects.get(id=comp_id)

    make_eval = CompanyEvaluation.objects.create(company=evaluate, hs_code=hs_code, description=description,
                                                 reference=ref, ref_date=ref_date, rate_1=quality,
                                                 rate_2=document, rate_3=response, rate_4=packing,
                                                 rate_5=recommend, total=total)

    if review != 'N/A':
        make_review = CompanyReviews.objects.create(company=evaluate, evaluation=make_eval, review=review
                                                    , have_review=True)
        if total < 50:
            make_claim = CompanyClaims.objects.create(claimer=evaluator, claimest=evaluate, evaluation=make_eval,
                                                      reviews=make_review, notif=True)
            CompanyActivity.objects.create(company=evaluator, evaluation=make_eval, reviews=make_review,
                                           claim=make_claim, ip=ip)
            return Response("done")
        CompanyActivity.objects.create(company=evaluator, evaluation=make_eval, reviews=make_review, ip=ip)

        return Response("done")
    else:
        if total < 50:
            make_claim = CompanyClaims.objects.create(claimer=evaluator, claimest=evaluate, evaluation=make_eval,
                                                      notif=True)
            CompanyActivity.objects.create(company=evaluator, evaluation=make_eval,
                                           claim=make_claim, ip=ip)
            return Response("done")
        CompanyActivity.objects.create(company=evaluator, evaluation=make_eval, ip=ip)

        return Response("done")


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def companyEvaluationRequest(request):
    comp_id = request.POST.get('id')
    hs_code = request.POST.get('hs_code')
    description = request.POST.get('description')
    ref = request.POST.get('ref')
    ref_date = request.POST.get('ref_date')
    ip = get_IP(request)
    evaluator = CompanyDetail.objects.get(company=request.user)
    evaluate = CompanyDetail.objects.get(id=comp_id)

    make_req = EvaluationRequest.objects.create(sender=evaluator, receiver=evaluate, hs_code=hs_code,
                                                description=description,
                                                reference=ref, ref_date=ref_date)
    CompanyActivity.objects.create(company=evaluator, request=make_req, ip=ip)

    return Response("done")


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def EvaluationRequestFilter(request):
    # ip = get_IP(request)
    evaluator = CompanyDetail.objects.get(company=request.user)

    instance = EvaluationRequest.objects.filter(receiver=evaluator, notif=False)
    data = {}
    if instance:
        data = EvaluationRequestSerializer(instance, many=True).data
    return Response(data)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def requestAddEvaluation(request):
    request_id = request.POST.get('id')
    quality = request.POST.get('quality')
    document = request.POST.get('document')
    response = request.POST.get('response')
    packing = request.POST.get('packing')
    recommend = request.POST.get('recommend')
    total = int(request.POST.get('total'))
    review = request.POST.get('review')
    ref_date = request.POST.get('ref_date')
    ip = get_IP(request)
    get_req = EvaluationRequest.objects.get(id=request_id)
    get_req.notif = True
    get_req.save()
    make_eval = CompanyEvaluation.objects.create(company=get_req.sender, hs_code=get_req.hs_code
                                                 , description=get_req.description,
                                                 reference=get_req.reference, ref_date=ref_date,
                                                 rate_1=quality,
                                                 rate_2=document, rate_3=response, rate_4=packing,
                                                 rate_5=recommend, total=total)
    if review != 'N/A':
        make_review = CompanyReviews.objects.create(company=get_req.sender, evaluation=make_eval, review=review
                                                    , have_review=True)
        if total < 50:
            make_claim = CompanyClaims.objects.create(claimer=get_req.sender, claimest=get_req.receiver,
                                                      evaluation=make_eval, reviews=make_review, notif=True)
            CompanyActivity.objects.create(company=get_req.receiver, evaluation=make_eval, reviews=make_review,
                                           claim=make_claim, ip=ip)
            return Response("done")
        CompanyActivity.objects.create(company=get_req.receiver, evaluation=make_eval, reviews=make_review, ip=ip)
        return Response("done")
    else:
        if total < 50:
            make_claim = CompanyClaims.objects.create(claimer=get_req.sender, claimest=get_req.receiver,
                                                      evaluation=make_eval,
                                                      notif=True)
            CompanyActivity.objects.create(company=get_req.receiver, evaluation=make_eval,
                                           claim=make_claim, ip=ip)
            return Response("done")
        CompanyActivity.objects.create(company=get_req.receiver, evaluation=make_eval, ip=ip)
        return Response("done")


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def claimFilter(request):
    get_comp = CompanyDetail.objects.get(company=request.user)

    instance = CompanyClaims.objects.filter(claimest=get_comp, notif=True)
    data = {}
    if instance:
        data = ClaimsSerializer(instance, many=True).data
        today = datetime.datetime.now().date()
    return Response(data)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def claimAction(request):
    request_id = request.POST.get('id')
    action = request.POST.get('action')
    today = datetime.datetime.now().date()

    get_claim = CompanyClaims.objects.get(id=request_id)
    get_claim.action = action
    get_claim.ref_date = today
    get_claim.notif = False
    get_claim.save()

    return Response('done')


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def profilEvaluation(request):
    get_comp = CompanyDetail.objects.get(company=request.user)
    get_count = CompanyEvaluation.objects.filter(company=get_comp).count()
    get_avr = CompanyEvaluation.objects.filter(company=get_comp).aggregate(priceAvg=Avg('total'))['priceAvg']
    get_post = CompanyEvaluation.objects.filter(company=get_comp, total__gte=60).count()
    get_neg = CompanyEvaluation.objects.filter(company=get_comp, total__lt=60).count()
    get_cust = CompanyActivity.objects.filter(evaluation__company=get_comp)
    cust = 0
    prev = 0
    for i in get_cust:
        if prev != i.company.id:
            cust = cust + 1
        prev = i.company.id
    send_data = {
        'count': get_count,
        'average': round(get_avr, 2),
        'positive': round((get_post / get_count) * 100, 2),
        'negative': round((get_neg / get_count) * 100, 2),
        'customers': cust,

    }

    return Response(send_data)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes([IsAuthenticated])
def contactUs(request):
    get_comp = CompanyDetail.objects.get(company=request.user)
    subject = request.POST.get('subject')
    message = request.POST.get('message')
    ContactSupport.objects.create(company=get_comp, subject=subject, message=message)
    return Response('done')
