from rest_framework import serializers
from neatApi.models import cityData, finData

class cityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = cityData
        fields = ['id','cityName','tz','temp_c','temp_f','humidity','conditionIcon']

class finDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = finData
        fields = ['id', 'symbol','lastRefresh','regularMarketPrice','previousClose','currency','downloadRefreshDate','dateHistoric','closeHistoric']
