import argparse
import os
import re
import requests
import time

def obtener_datos_por_ip(ip):
    uri = f"https://api.maclookup.app/v2/macs/d4:9d:c0"
    response, elapsed_time = realizar_solicitud(uri)
    fabricante = obtener_fabricante_desde_arp(response.text)

    if fabricante:
        print(f"IP address: {ip} Fabricante: {fabricante} Tiempo de respuesta: {round(elapsed_time*1000)}ms")
    else:
        print(f"IP address: {ip} No se encontró información del fabricante. Tiempo de respuesta: {round(elapsed_time*1000)}ms")

def obtener_datos_por_mac(mac):
    uri = f"https://api.maclookup.app/v2/macs/{mac}"
    response, elapsed_time = realizar_solicitud(uri)
    fabricante = response.json().get('company', '')
    return fabricante, elapsed_time

def realizar_solicitud(uri):
    start_time = time.time()
    response = requests.get(uri)
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000)
    return response, elapsed_time

def obtener_fabricante_desde_arp(arp_output):
    lines = arp_output.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            ip = parts[0]
            mac = parts[1]
            if ip.startswith("192.168.1.") and len(mac) == 17:
                return mac
def main():
    parser = argparse.ArgumentParser(description="Herramienta para consultar el fabricante de una tarjeta de red dada su dirección MAC o su IP.")
    parser.add_argument("--ip", help="IP del host a consultar.")
    parser.add_argument("--mac", help="MAC a consultar. P.e. aa:bb:cc:00:00:00.")
    parser.add_argument("--arp", help="Muestra los fabricantes de los host disponibles en la tabla arp.", action="store_true")
    parser.add_argument("--api", help="MAC a consultar usando la API. P.e. aa:bb:cc:00:00:00.")
    args = parser.parse_args()

    if args.mac:
        mac_address = args.mac
        vendor, elapsed_time = obtener_datos_por_mac(mac_address)
        if vendor:
            print(f"IP address: {mac_address} Fabricante: {vendor} Tiempo de respuesta: {elapsed_time}ms")
        else:
            print(f"No se encontró información del fabricante para la dirección MAC {mac_address}. Tiempo de respuesta: {elapsed_time}ms")
    elif args.ip:
        ip_address = args.ip
        obtener_datos_por_ip(ip_address)
    elif args.arp:
        response = os.popen("arp -a").read()
        arp_table = re.findall(r"((\d{1,3}\.){3}\d{1,3})\s+([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\s+(\w+)", response)
        print("IP/MAC/Vendor/Tiempo de respuesta:")
        for arp_entry in arp_table:
            ip_address, _, mac_address, _, _ = arp_entry
            vendor, elapsed_time = obtener_datos_por_mac(mac_address)
            if vendor:
                print(ip_address + " / " + mac_address + " / " + vendor + " / " + str(elapsed_time) + "ms")
            else:
                print(ip_address + " / " + mac_address + " / No se encontró información del fabricante. / " + str(elapsed_time) + "ms")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
