from django.conf import settings
import random
import string
import time, datetime

SHORTCODE_MIN = getattr(settings, "SHORTCODE_MIN", 15)

def code_generator(size = SHORTCODE_MIN,chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def logging(msg):
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    log = open("/var/log/subscribe.log","+a")
    log.write("{0} : {1}".format(timestamp, msg))
    log.close()