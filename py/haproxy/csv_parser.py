import aiohttp
import csv
import socket

class Haproxy:
    def __init__(self, session: aiohttp.ClientSession,credentials: dict[str, str]):
        self.session = session

    async def get(self, *args, **kwargs):
        async with self.session.request("GET", *args, **kwargs) as resp:
            return {
                "status": resp.status,
                "text": (await resp.read()).decode("utf-8")
            }

    async def getLoadBalancerByHostName(self, host_name: str) -> str:
        return socket.gethostbyname(host_name)

    async def haproxy_metrics(self, hostname, username, password):
        metrics = {}
        keys = []
        response = await self.get(f"{await self.getLoadBalancerByHostName(hostname)}:1222/stats;csv;norefresh", auth=(username, password))
        if response['status_code'] == 200:
            reader = csv.reader(StringIO(response['text']))
            for index, row in enumerate(reader):
                if index == 0:
                    if isinstance(row, list):
                        for entry in row:
                            keys.append(entry.replace("#", "").strip())
                else:
                    if row[0] not in metrics:
                        metrics[row[0]] = []
                    else:
                        metrics[row[0]].append({x:y for x, y in zip(keys[1:], row[1:])})
        return metrics
