from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
import requests
import os
import yfinance as yf


weatherApiKey = os.environ.get('weatherApiKey')
symbolList = ['^GSPC','^DJI','^N225','BTC-USD','JPY=X','EURUSD=X','GC=F','CL=F']

class neatData(models.Model):
    lastRefresh = models.DateTimeField(null=True, default=timezone.now)

class cityData(neatData):
    cityName = models.CharField(max_length=50)
    tz = models.CharField(max_length=50, null=True)
    temp_c = models.FloatField(null=True)
    temp_f = models.FloatField(null=True)
    humidity = models.FloatField(null=True)
    conditionIcon = models.URLField(null=True)

    def refresh(self):
        timeDiff = timezone.now() - self.lastRefresh
        if timeDiff > timedelta(seconds = 60):
            api_url = "http://api.weatherapi.com/v1/current.json"
            api_url += "?key="+weatherApiKey
            api_url += "&q="+self.cityName+"&aqi=yes"
            response = requests.get(api_url)
            self.lastRefresh = timezone.now()
            data = response.json()
            print(self.cityName + "data udpated at "+str(datetime.now()))
            self.tz = data['location']['tz_id']
            self.temp_c = str(data['current']['temp_c'])
            self.temp_f = str(data['current']['temp_f'])
            self.humidity = str(data['current']['humidity'])
            self.conditionIcon = data['current']['condition']['icon']
            self.save()

class finData(neatData):
    ### finData is called a single download of yFinannce ###
    symbol = models.CharField(max_length=50)
    dateRecent = models.DateTimeField(null=True)
    closeRecent = models.FloatField(null=True)
    openRecent = models.FloatField(null=True)

    dateHistoric = models.DateTimeField(null=True)
    closeHistoric = models.FloatField(null=True)

    @classmethod
    def refreshAll(cls):
        if len(cls.objects.all()) < len(symbolList):
            #TODO: better call from an init function, but urls.py annoyingly repeats itself
            cls.finDataInit()
        timeDiff = timezone.now() - cls.objects.all()[0].lastRefresh
        if timeDiff > timedelta(seconds=60):
            print("finData updating...")
            data = yf.download(tickers=symbolList, group_by='Ticker', period="1y", interval="3mo")

            for i in symbolList:
                finData_t = cls.objects.get(symbol=i)
                finData_t.lastRefresh=timezone.now()

                # use Adjusted Close as most important data
                adjClose = data[i]['Adj Close']

                # get most recent data
                idx_r = adjClose.last_valid_index()
                finData_t.closeRecent = adjClose[idx_r]
                finData_t.openRecent = data[i]['Open'][idx_r] #get 'Open' with most recent index
                finData_t.dateRecent = idx_r.tz_localize('UTC')

                # get most historic data
                idx_h = adjClose.first_valid_index()
                finData_t.dateHistoric = idx_h.tz_localize('UTC')
                finData_t.closeHistoric = adjClose[idx_h]
                finData_t.save()

    @classmethod
    def finDataInit(cls):
        ### create all objects if they are missing from list ###
        for i in symbolList:
            try:
                finData_t = cls.objects.get(symbol = i)
                print(i + "already exists")
            except:
                finData_t = cls()
                finData_t.symbol = i
                finData_t.lastRefresh = timezone.now()-timedelta(hours=1)
                finData_t.save()
                print("created new finData with symbol "+i)
