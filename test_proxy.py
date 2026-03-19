import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector

TEST_URL = "https://api.telegram.org"
PROXY_FILE = "socks5.txt"
TIMEOUT = 8
CONCURRENCY = 100  # сколько прокси проверять одновременно


def normalize_proxy(line: str):
    line = line.strip()

    if not line:
        return None, None, None

    if line.startswith("socks5://"):
        proxy_url = line
        raw = line.replace("socks5://", "", 1)
    else:
        raw = line
        proxy_url = f"socks5://{line}"

    if ":" not in raw:
        return None, None, None

    host, port = raw.rsplit(":", 1)
    return proxy_url, host, port


async def test_one(idx: int, line: str, semaphore: asyncio.Semaphore):
    proxy_url, host, port = normalize_proxy(line)

    if not proxy_url:
        return {
            "idx": idx,
            "ok": False,
            "proxy": line,
            "error": "неверный формат",
            "host": None,
            "port": None,
        }

    async with semaphore:
        try:
            connector = ProxyConnector.from_url(proxy_url)
            timeout = aiohttp.ClientTimeout(total=TIMEOUT)

            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(TEST_URL) as response:
                    text = await response.text()
                    return {
                        "idx": idx,
                        "ok": True,
                        "proxy": proxy_url,
                        "status": response.status,
                        "text": text[:120],
                        "host": host,
                        "port": port,
                    }
        except Exception as e:
            return {
                "idx": idx,
                "ok": False,
                "proxy": proxy_url,
                "error": str(e),
                "host": host,
                "port": port,
            }


async def main():
    try:
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Файл {PROXY_FILE} не найден.")
        return

    print(f"Найдено прокси: {len(proxies)}")
    print(f"Параллельная проверка, одновременно: {CONCURRENCY}\n")

    semaphore = asyncio.Semaphore(CONCURRENCY)

    tasks = [
        asyncio.create_task(test_one(idx, line, semaphore))
        for idx, line in enumerate(proxies, start=1)
    ]

    checked = 0

    for future in asyncio.as_completed(tasks):
        result = await future
        checked += 1

        if result["ok"]:
            print(f"[{result['idx']}] OK -> {result['proxy']} (status={result['status']})")
            print("\n✅ Рабочий прокси найден:")
            print(f"PROXY_HOST={result['host']}")
            print(f"PROXY_PORT={result['port']}")
            print("PROXY_USER=")
            print("PROXY_PASS=")
            print(f"\nОтвет Telegram API: {result['text']}\n")

            # отменяем остальные задачи
            for task in tasks:
                if not task.done():
                    task.cancel()
            return
        else:
            if checked % 20 == 0:
                print(f"Проверено: {checked}/{len(proxies)}")

    print("\n❌ Рабочих прокси не найдено.")


if __name__ == "__main__":
    asyncio.run(main())