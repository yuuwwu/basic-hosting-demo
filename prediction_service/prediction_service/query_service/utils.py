""" utility functions for query service """
import logging
import aiohttp


LOGGER = logging.getLogger()


async def download_file_async(url, destination):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()

        with open(destination, "wb") as file:
            file.write(content)

        LOGGER.info(f"UTIL - Downloaded file from {url} to {destination} successfully.")
    except aiohttp.ClientError:
        LOGGER.error(
            f"UTIL - Failed to download the file from {url} to {destination}",
            exc_info=True,
        )
