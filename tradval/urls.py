

from django.urls import path, include
from . import views

urlpatterns = [

    path('login/', views.loginUser, name="login"),
    path('signup/', views.createUser, name="signup"),
    path('profile/', views.profilEvaluation, name="profile"),
    path('lookup/', views.companySearch.as_view()),
    path('userlookup/', views.userCompanySearch.as_view()),
    path('createuser/', views.createUserByUser, name="createuser"),
    path('lookupresult/', views.evaluationResults, name="lookupresult"),
    path('lookupreviews/', views.evaluationPReviews, name="lookupreviews"),
    path('evaluation/', views.companyAddEvaluation, name="evaluation"),
    path('request/', views.companyEvaluationRequest, name="request"),
    path('filterrequest/', views.EvaluationRequestFilter, name="filterrequest"),
    path('closerequest/', views.requestAddEvaluation, name="closerequest"),
    path('claimFilter/', views.claimFilter, name="claimFilter"),
    path('claimAction/', views.claimAction, name="claimAction"),
    path('contactUs/', views.contactUs, name="contactUs"),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

]
