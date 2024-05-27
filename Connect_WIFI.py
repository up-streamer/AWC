import gc
import network
import time
import asyncio

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

async def do_connect():
    ssid = None
    psw = None
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
    elif  b'IoT' in names:
        ssid = IoT_SSID
        psw = IoT_PASSWORD

    if ssid != None:
        if not wlan.isconnected():
            print('connecting to network...' + ssid)
            wlan.connect(ssid, psw)
            s=wlan.status()
            print(s)

        start = time.ticks_ms()  # get millisecond counter
        while not wlan.isconnected():
            await asyncio.sleep(5)
            print(str(time.ticks_ms() - start))
            if time.ticks_ms() - start > 20000:
                print("connect timeout!")

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())
        gc.collect()
    return wlan
