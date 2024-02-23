import asyncio
import async_http as ahttp


async def main():
    posts = await asyncio.gather(ahttp.parse_bitrix())
    print(*posts[0], sep='\n\n')


if __name__ == '__main__':
    asyncio.run(main())
