import asyncio
import async_http as ahttp
import vk_parser as pp


async def main():
    parser = pp.Parser()
    posts = await asyncio.gather(ahttp.parse_bitrix())
    print(*posts[0], sep='\n\n')
    vk_posts = parser.parse_vk()
    print(*vk_posts, sep='\n\n')


if __name__ == '__main__':
    asyncio.run(main())
