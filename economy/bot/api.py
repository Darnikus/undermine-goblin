import aiohttp
from bot.config import API_BASE_URL


async def fetch_items():
    api_url = f"{API_BASE_URL}/items/"
    timeout = aiohttp.ClientTimeout(total=10.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "data": data}

                elif response.status == 404:
                    return {
                        "success": False,
                        "message": "No items found on the server.",
                    }

                elif 500 <= response.status < 600:
                    return {
                        "success": False,
                        "message": "The backend server encountered an error.",
                    }

    except TimeoutError:
        return {
            "success": False,
            "message": "The server took too long to respond.",
        }
    except aiohttp.ClientConnectorError:
        return {"success": False, "message": "Unable to reach the backend server."}
