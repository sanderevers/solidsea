# Solidsea

A simple [OIDC](https://openid.net/connect/) provider that federates to
other identity providers over OAuth1/OAuth2/OIDC. Solidsea does not use
a database/keystore; all state needed for the authentication flow is
either kept on the client using session cookie or encrypted into the
authorization code. This makes Solidsea very easy to deploy (and scale).

Out of the box, Solidsea federates to Github, Google and Twitter (when
provided with client credentials). This can be extended to other providers
without altering the source code.

When a user is directed to the `/authorize` endpoint, Solidsea shows an
(adaptable) choice screen. If a `?federate=github` parameter is added,
this screen is skipped.

This software is not related to the
[eponymous Danish pop group](https://solidsea.bandcamp.com/releases).

### Note on security

Solidsea is in a hobby phase. As with all open source software, no
guarantees are given. Most protocol functionality is handled by
[Authlib](https://authlib.org/) which I deem quite trustworthy.