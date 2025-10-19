
class Feedback():
    def __init__(self, parent, username, is_admin=False): 
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.is_admin = is_admin