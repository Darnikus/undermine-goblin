from dataclasses import dataclass
from typing import Literal, TypedDict

import aiohttp

from economy.bot.config import API_BASE_URL


class ItemData(TypedDict):
    """Represents the serialized item payload from an API call.

    Attributes:
        id (str): An item's ID.
        name (str): An item's name.
        display (str): An item's display text.
    """

    id: str
    name: str
    display: str


@dataclass(frozen=True)
class OkResponse[T]:
    """Represents a successful API response with a typed payload.

    Evaluates to `True` in boolean contexts, allowing static type checkers
    to automatically narrow `ApiResponse[T]` to `OkResponse[T]`.

    Attributes:
        data (T): The parsed payload of type `T`.
        success (Literal[True]): Always `True` to indicate a successful operation.
    """

    data: T
    success: Literal[True] = True

    def __bool__(self) -> Literal[True]:
        """Returns `True` to support truthiness check (`if response:`)."""
        return True


@dataclass(frozen=True)
class FailResponse:
    """Represents a failed API response with an error message.

    Evaluates to `False` in boolean contexts, allowing static type checkers
    to automatically narrow `ApiResponse[T]` to `FailResponse`.

    Attributes:
        message (str): A clear, easy-to-understand error message that can be
            shown directly to end users.
        success (Literal[False]): Always `False` to indicate a failed operation.
    """

    message: str
    success: Literal[False] = False

    def __bool__(self) -> Literal[False]:
        """Returns `False` to support truthiness checks (`if not response:`)."""
        return False


type ApiResponse[T] = OkResponse[T] | FailResponse
"""Discriminated union representing the outcome of an API call.

Use a standard truthiness check to narrow the type before accessing safely
attributes:

Example:

    >>> response = await fetch_items()
    >>> if response:
    ...     print(response.data)    # Narrowed to OkResponse[T]
    ... else:
    ...     print(response.message) # Narrowed to FailResponse
"""


async def create_item(id: str) -> ApiResponse[tuple[ItemData, bool]]:
    """Creates a new item using an ID or link.

    Args:
        id (str): An item's ID or a link containing an ID.

    Returns:
        ApiResponse[tuple[ItemData, bool]]: An `OkResponse` containing a
            `(ItemData, created)` tuple, where `created` is `True` if the
            item is created and `False` if it already exists; otherwise, a
            `FailResponse` with a validation or server error message.
    """
    api_url = f"{API_BASE_URL}items/"
    timeout = aiohttp.ClientTimeout(total=10.0)
    payload = {"id": id}

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 200:
                    item: ItemData = await response.json()
                    return OkResponse((item, False))

                elif response.status == 201:
                    data: ItemData = await response.json()
                    return OkResponse((data, True))

                elif response.status == 400:
                    error_payload: dict = await response.json()
                    message = error_payload.get("id", ["Invalid input."])[0]
                    return FailResponse(f"⚠️ {message}")

                return FailResponse(
                    "❌ The backend server encountered an error. "
                    f"Status code: {response.status}"
                )
    except TimeoutError:
        return FailResponse("❌ The server took too long to respond.")
    except aiohttp.ClientConnectorError:
        return FailResponse("❌ Unable to reach the backend server.")


async def delete_item(id: str) -> ApiResponse[ItemData]:
    """Removes the item from the tracked list.

    Args:
        id (str): An item's ID.

    Returns:
        ApiResponse[ItemData]: An `OkResponse` containing the `ItemData`
            dictionary on success, or a `FailSuccess` with a user-friendly
            error message on failure.
    """
    api_url = f"{API_BASE_URL}items/{id}/"
    timeout = aiohttp.ClientTimeout(total=10.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.delete(api_url) as response:
                if response.status == 200:
                    deleted_item: ItemData = await response.json()
                    return OkResponse(deleted_item)

                elif response.status == 404:
                    return FailResponse(f"⚠️ Item with ID: `{id}` was not found.")

                return FailResponse("❌ An error occurred while deleting the item.")

    except TimeoutError:
        return FailResponse("❌ The server took too long to respond.")
    except aiohttp.ClientConnectorError:
        return FailResponse("❌ Unable to reach the backend server.")


async def fetch_items() -> ApiResponse[list[ItemData]]:
    """Fetches all tracked items from the backend API.

    Returns:
        ApiResponse[list[ItemData]]: An `OkResponse[T]` containing a list of
            `ItemData` dictionaries (which may be empty), or an
            `FailResponse` with a user-friendly error message on failure.
    """
    api_url = f"{API_BASE_URL}items/"
    timeout = aiohttp.ClientTimeout(total=10.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data: list[ItemData] = await response.json()
                    return OkResponse(data)

                elif response.status == 404:
                    return FailResponse("❌ No items are currently being tracked.")

                return FailResponse(
                    "❌ The backend server encountered an error. "
                    f"Status code: {response.status}"
                )

    except TimeoutError:
        return FailResponse("❌ The server took too long to respond.")

    except aiohttp.ClientConnectorError:
        return FailResponse("❌ Unable to reach the backend server.")
