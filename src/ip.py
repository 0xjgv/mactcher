from urllib.request import Request, urlopen
from json import loads
import ipaddress


def get_current_ip():
    req = Request(url="https://ifconfig.co/json", headers={'User-Agent': 'curl/7.54.0'})
    return loads(urlopen(req).read().decode())


if __name__ == "__main__":
    print("IP")
    ip = get_current_ip()
    print(type(ip), ip)
