class Station:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def validate(self) -> bool:
        # Basic validation for the station URL
        return self.url.startswith("http://") or self.url.startswith("https://")
