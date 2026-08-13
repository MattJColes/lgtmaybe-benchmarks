class Client:
    """Service client."""

    def stream_events(self, cursor=None):
        return self._transport.stream(cursor)
