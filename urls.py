from django.urls import path
from neatApi import views
from neatApi.models import finData

urlpatterns = [
    path('cities/',views.city_list),
    path('cities/<str:cityName>',views.city_detail),
    path('fin/', views.fin_list),
    path('fin/<str:symbol>',views.fin_detail),
]
