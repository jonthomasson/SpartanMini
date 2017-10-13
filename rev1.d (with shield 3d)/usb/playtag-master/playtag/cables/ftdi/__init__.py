from d2xx import info
try:
    from d2xx_data import Jtagger
except ValueError:
    pass

def showdevs():
    print
    print "\n%d devices found:\n" % len(info)
    print str(info)
    print
    print "You may specify device by index number, serial number or description."
    print

