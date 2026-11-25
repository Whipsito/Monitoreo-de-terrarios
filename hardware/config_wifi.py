import network


SSID = "TerraPapu"
CLAVE_AP = "TerraPapu-ESP32"


def iniciar_red():
    if hasattr(network.WLAN, "IF_AP"):
        modo_ap, modo_sta = network.WLAN.IF_AP, network.WLAN.IF_STA
    else:
        modo_ap, modo_sta = network.AP_IF, network.STA_IF
    network.WLAN(modo_sta).active(False)
    red = network.WLAN(modo_ap)
    red.active(True)
    try:
        red.config(ssid=SSID, key=CLAVE_AP, security=3)  # WPA2-PSK
    except (TypeError, ValueError):
        red.config(essid=SSID, password=CLAVE_AP, authmode=3)
    # El punto de acceso ya tiene su IP y DHCP predeterminados.
    return red
