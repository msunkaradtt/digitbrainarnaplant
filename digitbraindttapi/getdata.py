import aiohttp


class GetData:
    async def __fetch(self, session, endpoint, params):
        async with session.get(endpoint, params=params) as r:
            if r.status != 200:
                r.raise_for_status()

            return await r.json()

    async def fetchEndpoint(self, endpoint, params={}):
        async with aiohttp.ClientSession() as session:
            res = await self.__fetch(session, endpoint, params)
            return res
