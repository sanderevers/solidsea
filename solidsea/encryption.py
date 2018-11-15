from jwcrypto import jwe, jwk
from jwcrypto.common import json_encode

class Encryption():

    def init_app(self, app):
        with app.open_instance_resource(app.config['IDP_JWT_PUB_KEY_PATH'], 'rb') as f:
            self.pubkey_data = f.read()
        self.pubkey = jwk.JWK.from_pem(self.pubkey_data)
        self.pubkey_json = self.pubkey.export_public()

        with app.open_instance_resource(app.config['IDP_JWT_PRIV_KEY_PATH'], 'rb') as f:
            privkey_data = f.read()
        self.privkey = jwk.JWK.from_pem(privkey_data)
        self.privkey_json = self.privkey.export_private()

    def encrypt_and_serialize(self, id_token):
        eprot = {'alg': 'RSA-OAEP', 'enc': 'A256GCM'}
        encrypted_id_token = jwe.JWE(id_token.encode('utf-8'), json_encode(eprot))
        encrypted_id_token.add_recipient(self.pubkey)

        return encrypted_id_token.serialize(compact=True)

    def deserialize_and_decrypt(self, auth_code):
        jwe_token = jwe.JWE()
        jwe_token.deserialize(auth_code, key=self.privkey)
        return str(jwe_token.payload, 'utf-8')

encryption = Encryption()