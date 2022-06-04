
class Level:
    def __init__(self, title, path, image, description) -> None:
        self.title = title
        self.description = description
        self.path  = path
        self.image = image
        

    def __eq__(self, o) -> bool:
        return self.title == o.title
    def __hash__(self) -> int:
        return hash(self.title)