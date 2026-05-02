# saml2_config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = 'https://sneezing-overhung-overlaid.ngrok-free.dev'

def get_saml_config(metadata_file_path):
    """
    Returns SAML config dynamically for any client.
    Called with each client's specific metadata file path.
    """
    return {
        'xmlsec_binary': '/usr/bin/xmlsec1',
        'entityid': f'{BASE_URL}/saml2/metadata/',
        'attribute_map_dir': os.path.join(BASE_DIR, 'attribute-maps'),
        'service': {
            'sp': {
                'name': 'Django SAML POC',
                'endpoints': {
                    'assertion_consumer_service': [
                        (
                            f'{BASE_URL}/saml2/acs/',
                            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
                        ),
                    ],
                    'single_logout_service': [
                        (
                            f'{BASE_URL}/saml2/ls/',
                            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                        ),
                    ],
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
            'local': [metadata_file_path],      # ← dynamic per client
        },
        'debug': 1,
        'key_file': os.path.join(BASE_DIR, 'private.key'),
        'cert_file': os.path.join(BASE_DIR, 'public.cert'),
    }


# Default config (kept for backward compatibility with SSOCircle POC)
SAML_CONFIG = get_saml_config(
    os.path.join(BASE_DIR, 'idp_metadata.xml')
)