import aiohttp


class GetData:
    async def __fetch(self, session, endpoint):
        async with session.get(endpoint) as r:
            if r.status != 200:
                r.raise_for_status()

            return await r.json()

    async def fetchEndpoint(self, endpoint):
        async with aiohttp.ClientSession() as session:
            res = await self.__fetch(session, endpoint)
            return res
