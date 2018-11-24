import json
import hashlib
from base64 import urlsafe_b64encode

from authlib.specs.rfc7516 import JWE
from authlib.specs.rfc7517 import JWK
from authlib.specs.rfc7518 import JWE_ALGORITHMS, JWK_ALGORITHMS

class Encryption():

    def init_app(self, app):
        with app.open_instance_resource(app.config['IDP_JWT_PUB_KEY_PATH'], 'rb') as f:
            self.pubkey_data = f.read()
        self.pubkey_jwk_dict = JWK(JWK_ALGORITHMS).dumps(self.pubkey_data, kty='RSA')

        with app.open_instance_resource(app.config['IDP_JWT_PRIV_KEY_PATH'], 'rb') as f:
            self.privkey_data = f.read()
        self.privkey_jwk_dict = JWK(JWK_ALGORITHMS).dumps(self.privkey_data, kty='RSA')

        self.add_rsa_thumbprint_sha256()


    def encrypt_and_serialize(self, id_token):
        eprot = {'alg': 'RSA-OAEP', 'enc': 'A256GCM'}
        return JWE(JWE_ALGORITHMS).serialize_compact(eprot,id_token.encode('utf-8'),self.pubkey_data)

    def deserialize_and_decrypt(self, auth_code):
        return str(JWE(JWE_ALGORITHMS).deserialize_compact(auth_code, self.privkey_data)['payload'],'utf-8')

    def add_rsa_thumbprint_sha256(self):
        """Adds the key thumbprint as specified by RFC 7638."""
        t={}
        for k in ['kty','n','e']:
            t[k] = self.pubkey_jwk_dict[k]
        msg = json.dumps(t, separators=(',',':'), sort_keys=True)
        digest = hashlib.sha256(msg.encode()).digest()
        b64_bytes = urlsafe_b64encode(digest)
        kid = str(b64_bytes,'utf-8').rstrip('=')
        self.pubkey_jwk_dict['kid'] = kid
        self.privkey_jwk_dict['kid'] = kid

encryption = Encryption()