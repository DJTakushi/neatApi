from django.urls import path
from neatApi import views

urlpatterns = [
    path('cities/',views.city_list, name="neatApiCities"),
    path('cities/<str:cityName>',views.city_detail),
    path('fin/', views.fin_list, name="neatApiFins"),
    path('fin/<str:symbol>',views.fin_detail),
]
