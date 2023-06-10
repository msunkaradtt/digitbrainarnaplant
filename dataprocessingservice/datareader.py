import asyncio
import aiohttp
from centrallogger import CentralLogger


class DataReader:
    def __init__(self, endPoints):
        self.endpoints_ = endPoints
        self.logger_ = CentralLogger("datareaderlogs")

    async def __fetch(self, session, endpoint):
        async with session.get(endpoint) as r:
            if r.status != 200:
                r.raise_for_status()
                self.logger_.logger_.error(
                    "Failed to get data with status code: " + str(r.status))
            return await r.json()

    async def __fetch_all(self, session, endpoints):
        tasks = []
        for endpoint in endpoints:
            task = asyncio.create_task(self.__fetch(session, endpoint))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
        return res

    async def fetch_main(self):
        async with aiohttp.ClientSession() as session:
            responses: list = await self.__fetch_all(session, self.endpoints_)
            self.tasksData_ = responses[0]
            self.toolsData_ = responses[1]
            self.machinesData_ = responses[2]
