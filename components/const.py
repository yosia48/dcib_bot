from urllib.parse import urljoin

DETECTIVE_CONAN_WORLD_URL = "https://www.detectiveconanworld.com/"
_DCW_URL = DETECTIVE_CONAN_WORLD_URL
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
DEFAULT_HEADERS = {"User-Agent": USER_AGENT}

WIKI_URL = urljoin(_DCW_URL, "wiki/")
WIKI_ANIME_URL = urljoin(WIKI_URL, "Anime")
