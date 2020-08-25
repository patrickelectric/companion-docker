#!/usr/bin/env python3
import argparse
import json
import requests


""" 
adapted from https://github.com/al4/docker-registry-list
"""

class TagFetcher:
    cache: dict = {}

    def get_token(self, auth_url, image_name):
        payload = {
            'service': 'registry.docker.io',
            'scope': 'repository:{image}:pull'.format(image=image_name)
        }

        r = requests.get(auth_url + '/token', params=payload)
        if not r.status_code == 200:
            print("Error status {}".format(r.status_code))
            raise Exception("Could not get auth token")

        j = r.json()
        return j['token']


    def fetch_versions(self, image_name, index_url=None, token=None):
        if image_name in self.cache:
            return self.cache[image_name]

        if index_url is None:
            index_url="https://index.docker.io"
        if token is None:
            token = self.get_token(auth_url="https://auth.docker.io", image_name=image_name)
        h = {'Authorization': "Bearer {}".format(token)}
        r = requests.get('{}/v2/{}/tags/list'.format(index_url, image_name),
                        headers=h)
        tags = r.json()["tags"]
        self.cache[image_name] = tags
        return tags


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('name', help='Name of image to list versions of')
    p.add_argument('-t', '--token',
                   help='Auth token to use (automatically fetched if not specified)')
    p.add_argument('-i', '--index-url', default='https://index.docker.io')
    p.add_argument('-a', '--auth-url', default='https://auth.docker.io')

    args = p.parse_args()
    token = args.token or get_token(
        auth_url=args.auth_url, image_name=args.name)

    versions = fetch_versions(args.name, args.index_url, token)
    print(json.dumps(versions, indent=2))
