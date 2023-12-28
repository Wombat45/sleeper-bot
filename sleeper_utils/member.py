class Member:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    def get_id(self):
        return self.user_id
    
    def get_username(self):
        return self.username

    def get_members(self):
        return self.members
