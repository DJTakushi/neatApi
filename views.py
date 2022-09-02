from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from neatApi.models import cityData, cityList, finData, symbolList
from neatApi.serializers import cityDataSerializer, finDataSerializer


@csrf_exempt
def city_list(request):
    cityData.refreshAll()
    if request.method == 'GET':
        cities = cityData.objects.all()
        serializer = cityDataSerializer(cities, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def city_detail(request, cityName):
    try:
        city = cityData.objects.get(cityName = cityName)
    except:
        city = cityData.createFromCityName(cityName)
        if cityName == None:
            return HttpResponse(status=404)
    city.refresh()
    if request.method =='GET':
        serializer = cityDataSerializer(city)
        return JsonResponse(serializer.data)

@csrf_exempt
def fin_list(request):
    finData.prepareData()
    if request.method == 'GET':
        fins = finData.objects.all()
        serializer = finDataSerializer(fins, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def fin_detail(request, symbol):
    finData.prepareData()
    try:
        fin = finData.objects.get(symbol = symbol)
    except:
        return HttpResponse(status=404)
    if request.method =='GET':
        serializer = finDataSerializer(fin)
        return JsonResponse(serializer.data)
