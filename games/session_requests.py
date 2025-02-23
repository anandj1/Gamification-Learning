from requests import Session
from urllib.parse import urljoin

class LiveServerSession(Session):
    def __init__(self, url_base=None, *args, **kwargs):
        super(LiveServerSession, self).__init__(*args, **kwargs)
        self.url_base = url_base

    def request(self, method, url, **kwargs):
        # Use urljoin to safely join the base URL and relative path
        modified_url = urljoin(self.url_base, url)
        return super(LiveServerSession, self).request(method, modified_url, **kwargs)
