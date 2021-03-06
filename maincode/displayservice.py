#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

def refreshDisplay():
    try:
        logging.info("epd7in5 Demo")
        
        epd = epd7in5.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
           
        logging.info("read temp bmp file")
        Himage = Image.open(os.path.join(picdir, 'temp.bmp'))
        epd.display(epd.getbuffer(Himage))
       
        logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        logging.info("Clear...")
        epd.init()
        epd.Clear()
        
        logging.info("Goto Sleep...")
        epd.sleep()
        epd7in5.epdconfig.module_exit()
        exit()
