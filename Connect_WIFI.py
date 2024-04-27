import gc
import network
import time

AUTH_OPEN = 0
AUTH_WEP = 1
AUTH_WPA_PSK = 2
AUTH_WPA2_PSK = 3
AUTH_WPA_WPA2_PSK = 4

City_SSID = "Ricardo "
City_PASSWORD = "a1b2c3d4"
Country_SSID = "SweetCountryHome"
Country_PASSWORD = "RicArd0!2E"
IoT_SSID = "IoT"
IoT_PASSWORD = "a1b2c3d4"

def do_connect():
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(dhcp_hostname='AWC')
    networks = wlan.scan()
    names = [i[0] for i in networks]
    s = wlan.config("mac")
    mac = '%02x:%02x:%02x:%02x:%02x:%02x'.upper() % (s[0], s[1], s[2], s[3], s[4], s[5])
    print("Local MAC:" + mac)  # get mac
    for name in names:
        print(name)

    if b'Ricardo ' in names:
        ssid = City_SSID
        psw = City_PASSWORD
    elif b'SweetCountryHome' in names:
        ssid = Country_SSID
        psw = Country_PASSWORD
    else:
        ssid = IoT_SSID
        psw = IoT_PASSWORD

    if not wlan.isconnected():
        print('connecting to network...' + ssid)
        wlan.connect(ssid, psw)

    start = time.ticks_ms()  # get millisecond counter
    while not wlan.isconnected():
        time.sleep(1)  # sleep for 1 second
        if time.ticks_ms() - start > 20000:
            print("connect timeout!")
            break

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())
        gc.collect()
    return wlan
