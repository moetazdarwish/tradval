
from rest_framework import serializers
from .models import *


class LogininSerializer(serializers.Serializer):
    key = serializers.CharField()
    company = serializers.CharField()

class CreatByUserSerializer(serializers.Serializer):
    id = serializers.CharField()
    company = serializers.CharField()

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyActivity
        fields = '__all__'



class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetail
        fields = ['id', 'name', 'country']

class EvaluationRequestSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField('get_sender')
    class Meta:
        model = EvaluationRequest
        fields = ['id','sender','hs_code','description','reference','ref_date']

    def get_sender(self, obj):
        return {
            "name": obj.sender.name,
        }


class ClaimsSerializer(serializers.ModelSerializer):
    claimer = serializers.SerializerMethodField('get_sender')
    evaluation = serializers.SerializerMethodField('get_evaluation')
    reviews = serializers.SerializerMethodField('get_reviews')
    class Meta:
        model = CompanyClaims
        fields = ['id','claimer','evaluation','reviews']

    def get_sender(self, obj):
        return {
            "name": obj.claimer.name,
        }
    def get_evaluation(self, obj):
        return {
            "eval": obj.evaluation.total,
        }
    def get_reviews(self, obj):
        try:
            return {
                "review": obj.reviews.review,
            }
        except:
            return {
                "review":  'No Review',
            }

