from json import load as json_load, dump as json_dump
from subprocess import Popen, PIPE
from datetime import datetime
from os import system, name
from atexit import register
from time import sleep
from re import sub


class MacGraph:
    GRAPH_PATH = "./graph.json"

    def __init__(self):
        self.graph = self._load_graph()
        register(self._save_graph)

    def _load_graph(self):
        try:
            with open(self.GRAPH_PATH, "r") as graph:
                print("Previous graph LOADED.")
                return json_load(graph)
        except Exception as exc:
            print("Previous graph NOT LOADED.")
            print(exc)
            return {}

    def _save_graph(self):
        with open(self.GRAPH_PATH, "w") as file:
            print("Saving graph...")
            json_dump(self.graph, file)
            print("Graph saved.")

    def _update_connections(self, stdout):
        connected, disconnected, new = 0, 0, 0
        previous_macs = {*self.graph.keys()}
        now = datetime.now().strftime("%H:%M:%S")

        print("New connected MACs:")
        for line in stdout.splitlines():
            ip, rest = line.split("at")
            mac, more = rest.split("on")
            ip = sub(r"[^0-9\.]", "", ip)
            mac = mac.strip().upper()

            if "(" not in mac or ")" not in mac:
                self.graph.setdefault(mac, {}).update(
                    last_seen=now, ip=ip, connected=True
                )
                if mac in previous_macs:
                    previous_macs.remove(mac)
                    connected += 1
                else:
                    print(">", mac)
                    new += 1
        print()

        print("Disconnected MACs:")
        for previous in previous_macs:
            self.graph[previous].update(connected=False)
            print(">", previous, f"last_seen: {self.graph[previous].get('last_seen')}")
            disconnected += 1
        print()

        return connected, disconnected, new

    def _arp(self):
        print("> (Address Resolution Protocol) started...")
        kwargs = {'stdout': PIPE, 'stderr': PIPE, 'universal_newlines': True}
        with Popen(['arp', '-a'], **kwargs) as proc:
            return proc.communicate()

    def _print(self):
        for mac, more in self.graph.items():
            print(f"MAC: {mac} - IPs: {more['ip']} - Last seen: {more['last_seen']}")

    def start(self):
        while True:
            self._run()
            sleep(10)

    def _run(self):
        stdout, stderr = self._arp()
        if name == "posix":
            system('clear')
        else:
            system('cls')

        if stderr:
            print("stderr", stderr)
        elif stdout:
            connected, disconnected, new = self._update_connections(stdout)
            print("Disconnected count:", disconnected)
            print("Connected count:", connected)
            print("New count:", new)


if __name__ == "__main__":
    mac = MacGraph()
    mac.start()

    # use to test
    # with open("./stdout.txt", "r") as stdout:
    #     output = parse_line_output(stdout.readlines())
