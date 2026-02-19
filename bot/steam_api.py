import aiohttp


async def get_game_by_steam_id(steam_id):
    """
    Fetch a game's basic info from Steam Store API by app id.

    Returns:
        dict: {"name": str, "steam_link": str}
        None: if the app id is invalid or the request fails
    """
    url = f"https://store.steampowered.com/api/appdetails?appids={steam_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                payload = await response.json()
    except Exception:
        return None

    app_entry = payload.get(str(steam_id))
    if not app_entry or not app_entry.get("success"):
        return None

    app_data = app_entry.get("data", {})
    name = app_data.get("name")
    if not name:
        return None

    return {
        "name": name,
        "steam_link": f"https://store.steampowered.com/app/{steam_id}/",
    }


async def search_games_by_name(query, limit=5):
    """
    Search Steam Store for games by title.

    Returns:
        list[dict]: [{"steam_id": int, "name": str, "steam_link": str}, ...]
        []: if no results or request fails
    """
    url = "https://store.steampowered.com/api/storesearch/"
    params = {
        "term": query,
        "l": "english",
        "cc": "US",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                payload = await response.json()
    except Exception:
        return []

    items = payload.get("items", [])
    results = []
    for item in items:
        steam_id = item.get("id")
        name = item.get("name")
        if not steam_id or not name:
            continue
        results.append(
            {
                "steam_id": int(steam_id),
                "name": name,
                "steam_link": f"https://store.steampowered.com/app/{steam_id}/",
            }
        )
        if len(results) >= limit:
            break

    return results
