from json import load as json_load, dump as json_dump
from subprocess import Popen, PIPE
from datetime import datetime
from os import system, name
from atexit import register
from time import sleep
from mactcher import ip
from re import sub

IPS_DIR = "ips"

# TODO:
# add curses
# from curses import initscr, endwin
# example:
#    def users(self, instances):
#        self._screen = initscr()
#        register(endwin)
#        # ...

#    def _handle_output(self, output):
#        self._screen.clear()
#        for i, line in enumerate(output.splitlines()):
#            self._screen.addstr(i, 2, line.strip())
#        self._screen.refresh()
#        # ...


class MacGraph:
    def __init__(self):
        self.info =ip.get_ip_info()
        self.ip = self.info.get("ip") or "10.0.0.11"
        self.inet = ip.get_inet()

        self.graph_path = f"./{IPS_DIR}/{self.ip}.json"
        self.graph = self._load_graph()
        register(self._save_graph)

    def _load_graph(self):
        try:
            with open(self.graph_path, "r") as graph:
                print("Previous graph LOADED.")
                return json_load(graph)
        except Exception as exc:
            print("Previous graph NOT LOADED.")
            print(exc)
            return {"info": self.info}

    def _save_graph(self):
        with open(self.graph_path, "w") as file:
            print("Saving graph...")
            json_dump(self.graph, file)
            print("Graph saved.")

    def _update_connections(self, stdout):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        connected, disconnected, new = 0, 0, 0
        previous_macs = {*self.graph.keys()}

        print("New connected MACs:")
        for line in stdout.splitlines():
            if "MAC" not in line:
                continue
            _, rest = line.split(": ", 1)
            mac, system = rest.split(" ", 1)

            system = sub(r"\(|\)", "", system.strip())
            mac = mac.strip()

            state = self.graph.get(mac, {})
            if state:
                is_connected = state.get('connected')
                if is_connected == False:
                    print("> Reconnected:", mac)
            self.graph[mac] = {**state, "last_seen": now, "connected": True, "system": system}

            if mac in previous_macs:
                previous_macs.remove(mac)
                connected += 1
            else:
                print(">", mac)
                new += 1
        print()

        print("Recently disconnected MACs:")
        for previous_mac in previous_macs:
            if previous_mac == "info":
                continue
            prev_state = self.graph.get(previous_mac)
            if prev_state.get('connected') == True:
                print(">", previous_mac)
            self.graph[previous_mac].update(connected=False)
            disconnected += 1
        print()

        return connected, disconnected, new

    def _nmap(self):
        kwargs = {'stdout': PIPE, 'stderr': PIPE, 'universal_newlines': True}
        with Popen(['sudo', 'nmap', '-sn', self.inet], **kwargs) as proc:
            return proc.communicate()

    def start(self):
        while True:
            print("> Loading Address Resolution Protocol...")
            self._run()
            sleep(15)

    def _run(self):
        stdout, stderr = self._nmap()
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
