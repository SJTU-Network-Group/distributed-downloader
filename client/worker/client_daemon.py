class client_daemon:
    def __init__(self, url: str) -> None:
        self.url = url
        self.server_set = set()

    @staticmethod
    def fetch_server_list(track_address: str, client_tracker_bind_port: str) -> None:
        # TODO: add server address to self.server_set
        pass

