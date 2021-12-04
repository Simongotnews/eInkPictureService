#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import time, locale, requests, json
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
 
def getWeatherData():
    api_key = "2ce2755440320466eabeef1f79df0500"
    lat = "48.89731"
    lon = "9.19161"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def unixToLocalDateTime(date, formatString):
    offset = 3600
    return datetime.utcfromtimestamp(date + offset).strftime(formatString) # '%Y-%m-%d %H:%M:%S'

def isNight(weather_data):
    sunrise = weather_data["current"]["sunrise"]
    sunset = weather_data["current"]["sunset"]
    current_unix = weather_data["current"]["dt"]
    current_time = int(unixToLocalDateTime(current_unix, "%H"))

    if(current_time <= 12):    # A.M.
        return (current_unix <= sunrise)
    else:                      # P.M.
        return (current_unix >= sunset)
    
def getSymbolByKey(key, weather_data):  
    
    # thunderstorm
    if key == "11d":
        return "/home/pi/eInkPictureService/maincode/static/gewitter.png"
    
    # drizzle/rain
    elif key == "10d" or key == "10n": #
        if isNight(weather_data):
            return "/home/pi/eInkPictureService/maincode/static/regen.png"
        else:
            return "/home/pi/eInkPictureService/maincode/static/regen_nacht.png"
        
    # snow
    elif key == "13d":
        return "/home/pi/eInkPictureService/maincode/static/schnee.png"
    
    # mist/smoke/haze/fog
    elif key == "50d":
        return "/home/pi/eInkPictureService/maincode/static/nebel.png"

    # clear
    elif key == "01d":
        return "/home/pi/eInkPictureService/maincode/static/sonne.png"
    elif key == "01d":
        return "/home/pi/eInkPictureService/maincode/static/klar_nacht.png"
        
    # clouds
    elif key == "02d":
        return "/home/pi/eInkPictureService/maincode/static/sonne_wolken.png"
    elif key == "02n":
        return "/home/pi/eInkPictureService/static/bewoelkt_nacht.png"
    elif key == "03d" or key == "03n" or key == "04d" or key == "04n":
        return "/home/pi/eInkPictureService/maincode/static/bewoelkt.png"
    
    else: 
        return "/home/pi/eInkPictureService/maincode/static/wechselhaft.png"
    
def refreshWeather():
    img = Image.new('RGB', (640, 384), color = 'white')

    weather_data = getWeatherData() # initialize weather data with request to OWM

    current_temp = int(weather_data["current"]["temp"])
    current_weather_condition = weather_data["current"]["weather"][0]["icon"]
    sunrise_time = unixToLocalDateTime(weather_data["current"]["sunrise"], '%H:%M')
    sunset_time  = unixToLocalDateTime(weather_data["current"]["sunset"], '%H:%M')

    hourly_forecast_list = list()
    for hourForecast in weather_data["hourly"]:
        forecast_time =  unixToLocalDateTime(hourForecast["dt"], '%H:%M')    
        forecast_temp = float(hourForecast["temp"])
        forecast_icon = hourForecast["weather"][0]["icon"]
        hourly_forecast_list.append([forecast_time, forecast_temp, forecast_icon])

    next_24_hours = hourly_forecast_list[1:26]
    df = pd.DataFrame(next_24_hours, columns = ['time', 'temp', 'icon'])

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.show(block=True)
    plt.tick_params(axis='x', direction="in",length=68, width=0.41, colors='black',
                   grid_color='black', grid_alpha=0.5)
    plt.tick_params(axis='y', direction="in",length=290, width=0.41, colors='black',
                   grid_color='black', grid_alpha=0.5)
    #plt.xlabel(loc="left", xlabel="notchanginganytning", color="white")
    #plt.plot(x="time",y="temp",ax=ax,color="black",label=False,legend=False,figsize=(5.2,1.25),fontsize=15)

    plot = df.plot(x="time",y="temp",ax=ax,color="black",label=False,legend=False,figsize=(3.2,1.0),fontsize=12) 
    plt.savefig("/home/pi/eInkPictureService/maincode/forecast_chart.png", bbox_inches = 'tight')
    plt.cla()
    plt.clf()
    # Datum und Uhrzeit
    locale.setlocale(locale.LC_TIME, "de_DE.utf8")

    bebas = "/home/pi/eInkPictureService/maincode/BebasNeue-Regular.ttf"
    louis = "/home/pi/eInkPictureService/maincode/Louis George Cafe.ttf"
    font_100 = ImageFont.truetype(bebas, 145)
    font_120 = ImageFont.truetype(bebas, 120)
    font_30 = ImageFont.truetype(bebas, 30)
    font_20 = ImageFont.truetype(bebas, 20)
    font_15 = ImageFont.truetype(bebas, 15)
    font_10 = ImageFont.truetype(louis, 15)

    draw = ImageDraw.Draw(img)

    # date
    currentDate = time.strftime("%a, %d.%b %H:%M")
    draw.text((3, -2), currentDate,(0,0,0),font=font_30)

    # weather forecast:
    forecast_chart = Image.open("/home/pi/eInkPictureService/maincode/forecast_chart.png")
    img.paste(forecast_chart, (315,165))
    forecast_chart_x = 460
    forecast_chart_y = 280
    forecast_chart_w = 35
    forecast_chart_h = 13
    draw.rectangle([(forecast_chart_x,forecast_chart_y),
    	(forecast_chart_x+forecast_chart_w,forecast_chart_y+forecast_chart_h)], 
    	fill=(255,255,255), outline=(255,255,255), width=0) # hide time label

    fc_icon_x_iter = 52
    fc_weather_symbol_cropFactor = 40

    for i in range(0,5):
        fc_icon = Image.open(getSymbolByKey(next_24_hours[i*5][2], weather_data))
        fc_icon = fc_icon.resize((int(fc_icon.width/fc_weather_symbol_cropFactor),
                                                int(fc_icon.height/(fc_weather_symbol_cropFactor))), Image.ANTIALIAS)
        img.paste(fc_icon, (335+(i*fc_icon_x_iter), 275))   

    # current weather
    weather_symbol = Image.open(getSymbolByKey(current_weather_condition, weather_data))
    weather_symbol_cropFactor = 8
    weather_symbol = weather_symbol.resize((int(weather_symbol.width/weather_symbol_cropFactor),
                                            int(weather_symbol.height/(weather_symbol_cropFactor))), Image.ANTIALIAS)
    img.paste(weather_symbol, (470, 0))
    current_temp_string = (str(current_temp) + "°").decode('utf8')
    if ((-10 < current_temp) and (current_temp < 10)):
        draw.text((355, -15), current_temp_string,(0,0,0),font=font_100)
    elif (current_temp <= -10):
        draw.text((320, -5), current_temp_string,(0,0,0),font=font_120)
    else:
        draw.text((320, -15), current_temp_string,(0,0,0),font=font_100)

    # sunrise and sunset
    sunrise_symbol = Image.open("/home/pi/eInkPictureService/maincode/static/sunrise.png")
    sunrise_symbol_crop_factor = 20
    sunrise_symbol = sunrise_symbol.resize((int(sunrise_symbol.width/sunrise_symbol_crop_factor),
                                            int(sunrise_symbol.height/(sunrise_symbol_crop_factor))), Image.ANTIALIAS)
    img.paste(sunrise_symbol, (326,130))
    draw.text((357, 133), sunrise_time,(0,0,0),font=font_20)

    sunset_symbol = Image.open("/home/pi/eInkPictureService/maincode/static/sunset.png")
    sunset_symbol_crop_factor = 20
    sunset_symbol = sunset_symbol.resize((int(sunset_symbol.width/sunset_symbol_crop_factor),
                                            int(sunset_symbol.height/(sunset_symbol_crop_factor))), Image.ANTIALIAS)
    img.paste(sunset_symbol, (400,130))
    draw.text((428, 133), sunset_time,(0,0,0),font=font_20)

    # Alerts 
    alert_y_start = 290
    alert_y_iter = 20
    alerts = weather_data["alerts"]
    print(alerts)
    for alert in alerts[:2]:
        alert_event = alert["event"]
        alert_desc = alert["description"]
        alert_start_time = unixToLocalDateTime(alert["start"], '%H')
        alert_end_time = unixToLocalDateTime(alert["end"], '%H')

        draw.text((0, (alert_y_start + alert_y_iter)), alert_event + " (" + alert_start_time + "-" + alert_end_time + ") " + alert_desc, (0,0,0),font=font_10)
    
        if alert_desc.find("\n") == -1:
            alert_y_start = alert_y_start + alert_y_iter
        else:
            alert_y_start = alert_y_start + alert_y_iter + alert_y_iter

    # todo: load from notes.txt file into list
    # print last x notes from list
    notes_start_x = 10
    notes_start_y = 35
    notes_iter = 0
    notes = list()
    notes.append("Müll rausbringen")
    notes.append("TB machen..")
    notes.append("Wohnung Saugen")
    notes.append("Pia fragen, ob ich bald nochmal\n bei ihr Baden Darf?")
    notes.append("Bad putzen")
    notes.append("Weltherrschaft an dich reißen!")
    notes.append("Steuererklärung bis 31.12!!!")

    for note in notes:
        draw.multiline_text((notes_start_x, notes_start_y + notes_iter), "- " + note.decode('utf8'), font=font_20, fill=(0, 0, 0))
        if note.find("\n") == -1:
            notes_iter = notes_iter + 20
        else:
            notes_iter = notes_iter + 43

    draw.rectangle([(0, 0), (img.width-1, img.height-1)], fill=None, outline=(255,0,0), width=1)

    # dividingline
    xOff = 7
    draw.line(((img.width/2)-xOff,15, (img.width/2)-xOff, img.height-100), fill=0, width=2)
    #display(img)
    img.save("weather.png")
