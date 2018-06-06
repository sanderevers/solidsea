from authlib.specs.oidc.grants.base import UserInfo

class User():
    def __init__(self, sub):
        self.sub = sub

    def __str__(self):
        return self.sub

    def get_user_id(self):
        return self.sub

    def generate_user_info(self,scopes):
        return UserInfo(sub=self.sub)
