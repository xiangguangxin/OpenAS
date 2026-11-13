#!/usr/bin/env python3
"""Read GitHub pull-request review threads and their replies via gh."""
import argparse
import json
import re
import subprocess
import sys

THREADS = """
query($owner: String!, $repo: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      id url headRefOid
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line originalLine diffSide
          comments(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes { id url body createdAt author { login } }
          }
        }
      }
    }
  }
}
"""

REPLIES = """
query($id: ID!, $cursor: String) {
  node(id: $id) {
    ... on PullRequestReviewThread {
      comments(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { id url body createdAt author { login } }
      }
    }
  }
}
"""

HEAD = """
query($id: ID!) {
  node(id: $id) { ... on PullRequest { headRefOid } }
}
"""


def graphql(query, **variables):
    args = ['gh', 'api', 'graphql', '-f', f'query={query}']
    for key, value in variables.items():
        if value is not None:
            args.extend(['-F' if isinstance(value, int) else '-f', f'{key}={value}'])
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError(f'gh api graphql failed: {result.stderr.strip()}')
    payload = json.loads(result.stdout)
    if payload.get('errors') or not isinstance(payload.get('data'), dict):
        raise ValueError(f'GitHub GraphQL returned errors: {payload.get("errors")}')
    return payload['data']


def pages(fetch, first=None):
    page = first if first is not None else fetch(None)
    seen_nodes = set()
    seen_cursors = set()
    while True:
        for item in page['nodes']:
            identifier = item['id']
            if identifier not in seen_nodes:
                seen_nodes.add(identifier)
                yield item
        info = page['pageInfo']
        if not info['hasNextPage']:
            return
        cursor = info['endCursor']
        if not cursor or cursor in seen_cursors:
            raise ValueError('GitHub review pagination did not advance')
        seen_cursors.add(cursor)
        page = fetch(cursor)


def read_threads(owner, repo, number):
    def fetch_pr(cursor):
        data = graphql(THREADS, owner=owner, repo=repo, number=number, cursor=cursor)
        return data['repository']['pullRequest']

    first = fetch_pr(None)
    head = first['headRefOid']

    def thread_page(cursor):
        pr = fetch_pr(cursor)
        if pr['headRefOid'] != head:
            raise ValueError('PR head changed during thread collection')
        return pr['reviewThreads']

    threads = []
    for node in pages(thread_page, first['reviewThreads']):
        thread = {key: value for key, value in node.items() if key != 'comments'}
        thread['comments'] = list(pages(
            lambda cursor: graphql(REPLIES, id=node['id'], cursor=cursor)['node']['comments'],
            node['comments'],
        ))
        threads.append(thread)
    if graphql(HEAD, id=first['id'])['node']['headRefOid'] != head:
        raise ValueError('PR head changed during thread collection')
    return {'url': first['url'], 'head_sha': head, 'threads': threads}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', help='GitHub owner/repository')
    parser.add_argument('number', type=int, help='pull request number')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo) or args.number < 1:
        parser.error('expected owner/repository and a positive pull request number')
    try:
        payload = read_threads(*args.repo.split('/'), args.number)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f'Could not read review threads: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
