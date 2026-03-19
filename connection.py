def do_connect():
    import network
    from time import sleep
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('suman', '12345678')
        while not wlan.isconnected():
            print(". ", end='')
            sleep(.5)
    print('network config:', wlan.ipconfig('addr4'))

