from urllib.request import Request, urlopen
from subprocess import check_output
from ipaddress import ip_address
from time import sleep
from json import loads


def get_inet():
    output = check_output(["ifconfig", "en0", "inet"])
    for line in output.decode().splitlines():
        if "inet" in line:
            _, inet = line.strip().split()[:2]
            if ip_address(inet).is_private:
                vals = inet.split(".")[:-1] + ["*"]
                return ".".join(vals)
            else:
                print(line)
            return inet
    return ""


def get_ip_info(retry_times=0):
    if retry_times == 0:
        print("Getting IP info...")
    else:
        print("Retrying...")
        sleep(3)
    req = Request(url="https://ifconfig.co/json", headers={'User-Agent': 'curl/7.54.0'})
    try:
        res = urlopen(req).read()
        return loads(res.decode())
    except Exception as exc:
        if retry_times < 5:
            return get_ip_info(retry_times=retry_times+1)
        return {}


if __name__ == "__main__":
    info = get_inet()
    print(info)
    print("Current IP:", info)
