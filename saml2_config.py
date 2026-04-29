import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAML_CONFIG = {
    'xmlsec_binary': '/usr/bin/xmlsec1',  # May differ (See Note below)
    'entityid': 'https://sneezing-overhung-overlaid.ngrok-free.dev/saml2/metadata/',
    'attribute_map_dir': os.path.join(BASE_DIR, 'attribute-maps'),
    'service': {
        'sp': {
            'name': 'Django SAML POC',
            'endpoints': {
            "assertion_consumer_service": [
                ("https://sneezing-overhung-overlaid.ngrok-free.dev/saml2/acs/", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"),
            ],
            "single_logout_service": [
                ("https://sneezing-overhung-overlaid.ngrok-free.dev/saml2/ls/", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"),
            ]
            },
            'allow_unsolicited': True,
            'authn_requests_signed': False,
            'logout_requests_signed': False,
            'want_assertions_signed': False,
            'want_response_signed': False,
            'name_id_format': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
        }
    },
    'metadata': {
        'local': [os.path.join(BASE_DIR, 'idp_metadata.xml')],
    },
    'debug': 1,
    'key_file': os.path.join(BASE_DIR, 'private.key'),
    'cert_file': os.path.join(BASE_DIR, 'public.cert'),
}