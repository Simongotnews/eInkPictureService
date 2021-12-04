#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, time, threading, random
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, url_for
from displayservice import refreshDisplay
from weather import refreshWeather
from PIL import Image
import qrcode
from qrcode.image.pure import PymagingImage
#import calendar

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp', ''])
UPLOAD_FOLDER = './../pic'
PIC_PATH = "/home/pi/eInkPictureService/pic/"
WEATHER_PATH = "/home/pi/eInkPictureService/maincode/"
SLIDESHOW_PATH = "/home/pi/eInkPictureService/slideshow_images/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def prepareImagefromPath(filepath):
	rawImage = Image.open(filepath)
	rawImage = rawImage.convert('L')
	rawImage = rawImage.resize((640,384), Image.ANTIALIAS)
	rawImage.save(PIC_PATH + "temp.bmp")
	display_thread = threading.Thread(target=async_refresh_display, name="Display_Refresh")
	display_thread.start()

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
	return 'still alive'

@app.route('/calendar', methods=['GET'])
def refreshCalendar():
	print 'refreshing Calendar'
	return 'refreshing Calendar'

@app.route('/slideshow', methods=['GET'])
def slideshow():
	prepareImagefromPath(SLIDESHOW_PATH + random.choice(os.listdir(SLIDESHOW_PATH)))
	return "slideshow loading"

@app.route('/weather', methods=['GET'])
def showWeatherScreen():
	refreshWeather()
	prepareImagefromPath(WEATHER_PATH + 'weather.png')
	return 'generating and weather info screen'

@app.route('/qrcode', methods=['POST'])
def generate_and_show_qr():
    raw_json = request.get_json(force=True)
    qr_data = raw_json["qr_data"]
    print 'generating and showing QR code with data: ' + qr_data 

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
     )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(PIC_PATH + 'qr.png')

    rawImage = Image.open(PIC_PATH + 'qr.png')
    rawImage = rawImage.convert('L')
    rawImage = rawImage.resize((640,384), Image.ANTIALIAS)
    rawImage.save(PIC_PATH + "temp.bmp")
    display_thread = threading.Thread(target=async_refresh_display, name="Display_Refresh")
    display_thread.start()

    return 'generating and showing QR code ' + qr_data 

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print 'No file part'
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print 'No selected file'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # open rename and image in case its not already .bmp
            rawImage = Image.open("/home/pi/eInkPictureService/pic/" + filename)
            rawImage = rawImage.convert('L')
            rawImage = rawImage.resize((640,384), Image.ANTIALIAS)
            rawImage.save(PIC_PATH + "temp.bmp")
            display_thread = threading.Thread(target=async_refresh_display, name="Display_Refresh")
            display_thread.start()
            return 'upload done'
        else: 
            print 'File is not valid'
    return "wrong method"

def async_refresh_display():
	print "refreshing Display"
	refreshDisplay()
	print "done."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='1337')