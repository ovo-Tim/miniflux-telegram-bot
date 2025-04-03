import miniflux
import os

CLIENT = None

class articleType:
    def __init__(self, title: str, url: str, source:str, publish_time: str, id: int, content: str|None=None, comment: str|None=None, tags=None):
        self.title = title
        self.url = url
        self.source = source
        self.publish_time = publish_time
        self.id = id
        self.content = content
        self.comment = comment
        self.tags = tags

def init_miniflux(url: str|None=None, token: str|None=None):
    global CLIENT
    url = os.getenv("MINIFLUX_URL") if url is None else url
    token = os.getenv("MINIFLUX_TOKEN") if token is None else token

    if url is None or token is None:
        raise ValueError("MINIFLUX_URL or MINIFLUX_TOKEN is not set")

    CLIENT = miniflux.Client(url, api_key=token)

def get_started(limit: int=30) -> list[articleType]:
    data = CLIENT.get_entries(starred=True, limit=limit)
    if data is None:
        return []
    return [articleType(entry['title'], entry['url'], entry['feed']['title'], entry['published_at'], entry['id'],
                    entry['content'] if "hnrss.org" not in entry['feed']['feed_url'] else None,
                    entry['comments_url'], entry['tags'])
                    for entry in data["entries"]]

def mark_read(a: articleType):
    # Mark as readed and unstarred
    return CLIENT.toggle_bookmark(a.id)

def get_status():
    return f"Miniflux: {CLIENT.get_version()} \n URL: {os.getenv('MINIFLUX_URL')} \n User: {CLIENT.me()}"

if __name__ == "__main__":
    init_miniflux()
    print(get_started())