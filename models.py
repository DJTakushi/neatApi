from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
import requests
import os
import yfinance as yf

cityList = ['Osaka','Atlanta','Chicago']
weatherApiKey = os.environ.get('weatherApiKey')
symbolList = ['^GSPC','^DJI','^N225','BTC-USD','JPY=X','EURUSD=X','GC=F','CL=F']

refreshTickerPeriod = timedelta(minutes = 1)
refreshDownloadPeriod = timedelta(minutes = 5)
refreshCityPeriod = timedelta(minutes = 5)

class neatData(models.Model):
    lastRefresh = models.DateTimeField(null=True, default=timezone.now)

class cityData(neatData):
    cityName = models.CharField(max_length=50)
    tz = models.CharField(max_length=50, null=True)
    temp_c = models.FloatField(null=True)
    temp_f = models.FloatField(null=True)
    humidity = models.FloatField(null=True)
    conditionIcon = models.URLField(null=True)

    def isExpired(self):
        output = True
        if self.lastRefresh != None:
            dataAge = timezone.now() - self.lastRefresh
            if dataAge < refreshCityPeriod:
                output = False
        else:
            pass
        return output
    def refresh(self):
        if self.isExpired():
            print("refreshing "+self.cityName+"")
            api_url = "http://api.weatherapi.com/v1/current.json"
            api_url += "?key="+weatherApiKey
            api_url += "&q="+self.cityName+"&aqi=yes"
            response = requests.get(api_url)
            self.lastRefresh = timezone.now()
            data = response.json()
            self.tz = data['location']['tz_id']

            self.temp_c = str(data['current']['temp_c'])
            self.temp_f = str(data['current']['temp_f'])
            self.humidity = str(data['current']['humidity'])
            self.conditionIcon = data['current']['condition']['icon']
            self.save()

    @classmethod
    def refreshAll(cls):
        for i in cls.objects.all():
            i.refresh()
    @classmethod
    def createFromCityName(cls, cityName):
        output = None
        if cityName in cityList:
            city = cls()
            city.cityName = cityName
            city.save()
            city.refresh()
            output = city
        return output
    @classmethod
    def init(cls):
        # delete any objects not in the list #
        for i in cls.objects.all():
            if i.cityName not in cityList:
                print("deleting "+i.cityName)
                i.delete()

        # create any objects that are missing #
        for i in cityList:
            try:
                cls.objects.get(cityName=i)
            except:
                cls.createFromCityName(i)

class finData(neatData):
    ### finData is called a single download of yFinannce ###
    symbol = models.CharField(max_length=50)
    regularMarketPrice = models.FloatField(null=True)
    previousClose = models.FloatField(null=True)
    currency = models.CharField(max_length=10,null=True)


    downloadRefreshDate = models.DateTimeField(null=True)
    dateHistoric = models.DateTimeField(null=True)
    closeHistoric = models.FloatField(null=True)

    @classmethod
    def prepareData(cls):
        ## prepareData - can be called
            # - refreshDownload
            #     - refreshDownloadApproprite
            #         - closeHistoric
            #         - dateHistoric
            #         - downloadRefreshDate
            # - refreshTicker
            #     - refreshTickerAppropriate
            #         - regularMarketPrice
            #         - Previous Close
            #         - currency
            #         - lastRefresh*
            #         - open (maybe unnecessary)
            # - objectsAppropriate
        if not cls.validateObjects():
            cls.deleteAll()
            cls.init()

        cls.refreshDownload()
        for i in cls.objects.all():
            i.refreshTicker()

    @classmethod
    def refreshDownload(cls):
        if finData.refreshDownloadAppropriate():
            print("finData download updating...")
            data = yf.download(tickers=symbolList, group_by='Ticker', period="1y", interval="3mo")

            for i in symbolList:
                finData_t = cls.objects.get(symbol=i)

                # get most historic data
                dataSymbol = data[i]
                idx_h = dataSymbol.first_valid_index()
                finData_t.dateHistoric = idx_h.tz_localize('UTC')
                finData_t.closeHistoric = dataSymbol['Adj Close'][idx_h]
                finData_t.downloadRefreshDate=timezone.now()
                finData_t.save()

    @classmethod
    def refreshDownloadAppropriate(cls):
        output = False
        myO = cls.objects.all()[0]
        if myO.downloadRefreshDate:
            output = output or (timezone.now() - myO.downloadRefreshDate > refreshDownloadPeriod)
            output = output or myO.dateHistoric == None
            output = output or myO.closeHistoric == None
        else:
            output = True
        return output


    def refreshTicker(self):
        ### refresh using 'ticker' for just this object's symbol to get key data readily available in a 'download' ###
        if self.refreshTickerAppropriate():
            print("refreshing "+self.symbol+"...")
            self.lastRefresh = timezone.now()
            data_i = yf.Ticker(self.symbol).info
            self.regularMarketPrice = data_i['regularMarketPrice']
            self.previousClose=data_i['previousClose']
            self.currency = data_i['currency']
            self.save()

    def refreshTickerAppropriate(self):
        ### check if this object is 'expired'.  Expires after a full day.
        output = False
        output = output or self.lastRefresh == None
        output = output or self.regularMarketPrice == None
        output = output or self.previousClose == None
        output = output or self.currency == None
        output = output or ((timezone.now()-self.lastRefresh)) > refreshTickerPeriod
        return output

    @classmethod
    def init(cls):
        ### create all objects if they are missing from list ###
        print("finData.init()...")
        for i in cls.objects.all():
            if i.symbol not in symbolList:
                print("deleting "+i.symbol)
                i.delete()
        for i in symbolList:
            try:
                finData_t = cls.objects.get(symbol = i)
                if i.isSlowUpToDate() == False:
                    finData_t.slowRefresh()
            except:
                finData_t = cls()
                finData_t.symbol = i
                finData_t.lastRefresh = timezone.now()-timedelta(hours=1)
                finData_t.save()
                print("created new finData with symbol "+i)
        cls.refreshDownload()

    @classmethod
    def deleteAll(cls):
        print("finData.deleteAll()...")
        for i in cls.objects.all():
            i.delete()
        print("finData count = " + str(len(cls.objects.all())))

    @classmethod
    def validateObjects(cls):
        output = True
        if len(cls.objects.all()) != len(symbolList):
            output = output and False
        else:
            for i in symbolList:
                try:
                    cls.objects.get(symbol=i)
                except:
                    output = output and False
        return output
