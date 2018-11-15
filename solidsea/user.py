class User():
    def __init__(self, user_id, user_info):
        self.user_id = user_id
        self.user_info = user_info

    def __str__(self):
        return self.user_id

    def get_user_id(self):
        return self.user_id

    def generate_user_info(self,scopes):
        return self.user_info
