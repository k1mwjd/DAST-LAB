import os
import re
import sys
import time

import requests

TARGET = os.environ.get('TARGET', 'http://127.0.0.1').rstrip('/')
SETUP = f'{TARGET}/setup.php'


def get_token(html):
    match = re.search(r"""name=['"]user_token['"]\s+value=['"]([^'"]+)['"]""", html)
    if not match:
        sys.exit('[!] Could not find the CSRF token on the DVWA setup page')
    return match.group(1)


def main():
    with requests.Session() as session:
        for _ in range(60):
            try:
                page = session.get(SETUP, timeout=5)
                if page.status_code == 200:
                    break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            print('[*] Waiting for DVWA...')
            time.sleep(5)
        else:
            sys.exit('[!] DVWA did not start')

        response = session.post(SETUP, data={
            'create_db': 'Create / Reset Database',
            'user_token': get_token(page.text),
        }, timeout=30)
        response.raise_for_status()

    if 'Setup successful' not in response.text:
        sys.exit('[!] Database setup failed')

    print('[*] DVWA database created')


if __name__ == '__main__':
    main()
