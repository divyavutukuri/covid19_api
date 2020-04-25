from django.shortcuts import render
import requests
# Create your views here.
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as ur
import requests
import json
import pycountry
from collections import OrderedDict
from rest_framework.response import Response
from rest_framework import generics
def scrapping():
    URL = 'https://www.worldometers.info/coronavirus/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    page = requests.get(URL, headers=headers)
    soup = bs(page.content, 'html.parser')
    table_body = soup.find('table')
    rows = table_body.find_all('tr')
    l = []
    d = OrderedDict()

    f = {
        "Main": []
    }
    # to find the Main Header
    ss = []
    mains = soup.findAll("div", {"id": "maincounter-wrap"})

    for i in mains:
        ss.append(i.find("span").text)
    temp = soup.find_all("div", {"class": "panel_flip"})
    data1 = []
    data2 = []
    for k in temp:
        x = k.findAll("div", {"class": "number-table-main"})
        for i in x:
            data1.append(i.text.strip())
        m = k.findAll("span")
        for j in m:
            data2.append(j.text.strip())

    # print(temp1)
    cuinf, cloc = data1
    mild, seri, dis, dea = data2
    coc, cocd, rec = ss
    f["Main"].append({
        "CoronaCases": coc,
        "CoronaCurrent": cuinf,
        "CoronaClose": cloc,
        "CoronaMild": mild,
        "CoronaCritical": seri,
        "CoronaDischarged": dis,
        "CoronaDeaths": dea,
        "CoronaDeaths": cocd,
        "Recoverd": rec
    })

    # To get table data

    # To get table data
    mapping = {country.name: country.alpha_2 for country in pycountry.countries}
    for row in rows:
        cols = row.find_all('td')
        z = ['0' if v.text.strip() == "" else v.text.strip() for v in cols]

        # print(z)
        if len(z) != 0:
            c, totc, newc, totd, newd, totrecv, Actcases, seri, avg, Avgd, *x = z

            d[c] = OrderedDict()

            d[c]["Code"]=str(mapping.get(c)).lower()
            d[c]["TotalCases"] =totc

            d[c]["NewCases"]= newc
            d[c]["TotalDeaths"]=totd
            d[c]["NewDeaths"]= newd
            d[c]["TotalRecoverd"]=totrecv
            d[c]["ActiveCases"]=Actcases
            d[c]["Serious"]= seri
            d[c]["Average"]=avg
            d[c]["AverageDeaths"]=Avgd






    return [d,f]

class apiOverview(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        api_urls = {
            'Api':'GET || Summary of World data',
            'Api/all':'GET || Data of all countries together',
            'Api/countries':'GET || Summary of particular country'
            }
        a_urls=json.dumps(api_urls)
        data1 = {"Success": a_urls}
        return Response(data1)

def index(req):
    d=scrapping()[0]
    f=scrapping()[1]
    # d_j=d.json()
    # f_j=f.json()
    error=False
    cases,today_cases,deaths,today_deaths,active,serious='','','','','',''
    if req.method=="POST" and not req.POST["country"]=="":
        temp=req.POST["country"]
        a=type(temp)
        x=d.get(temp,0)
        if(x!=0):
            # print(temp)
            # print(a)
            # print(d)
            # country=x.get('Country')
            # print(x)
            cases=x.get('TotalCases')
            today_cases=x.get('NewCases')
            deaths=x.get('TotalDeaths')
            today_deaths=x.get('NewDeaths')
            active=x.get('ActiveCases')
            serious=x.get('Serious')
            error=False

        else:
            error=True
            print(temp)

    else:
        for x in f['Main']:
            error=False
            # country =x['Country']
            cases+=x['CoronaCases']
            today_cases=''
            deaths+=x['CoronaDeaths']
            today_deaths=''
            active+=x['CoronaCurrent']
            serious+=x['CoronaCritical']
    if error:
        data={"error":error,"cases":cases,"today_cases":today_cases,"deaths":deaths,"today_deaths":today_deaths,"active":active,"serious":serious}
    else:
        data={"cases":cases,"today_cases":today_cases,"deaths":deaths,"today_deaths":today_deaths,"active":active,"serious":serious}
    return render(req, 'covid19/index.html', context=data)

class CountryOverView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        data=scrapping()[0]

        data1 = {"Success": data}
        return Response(data1)

class CountryView(generics.ListAPIView):
    def get(self,request,country="India",*args,**kwargs):
        data=scrapping()[0]
        temp=data.get(country,0)
        if(temp):
            DataIndia=json.dumps(temp)
        else:
            DataIndia="null"
        if DataIndia=="null":
            return Response({"error":"Please Provide Valid Country Name"})
        data1={"Success":DataIndia}
        return Response(data1)
class GlobalView(generics.ListAPIView):
    def get(self,request,*args,**kwargs):
        data=json.dumps(scrapping()[1]['Main'])
        data1={"Success":data}
        return Response(data1)




