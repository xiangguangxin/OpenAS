import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1]/'plugins/openas/skills/pr-review-feedback/scripts/read_threads.py'
SPEC = importlib.util.spec_from_file_location('read_threads', SCRIPT)
reader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader)


def page(nodes, cursor=None):
    return {'nodes': nodes, 'pageInfo': {'hasNextPage': cursor is not None, 'endCursor': cursor}}


class ReviewThreadTests(unittest.TestCase):
    def test_threads_and_replies_advance_independently_and_deduplicate(self):
        first = {'id': 'T1', 'isResolved': False, 'comments': page([{'id': 'C1'}], 'reply-2')}
        second = {'id': 'T2', 'isResolved': True, 'comments': page([{'id': 'C3'}])}
        calls = []

        def graphql(query, **args):
            calls.append((query, args.get('cursor')))
            if query == reader.HEAD:
                return {'node': {'headRefOid': 'abc'}}
            if query == reader.REPLIES:
                self.assertEqual(args['id'], 'T1')
                return {'node': {'comments': page([{'id': 'C1'}, {'id': 'C2'}])}}
            threads = page([first], 'thread-2') if args['cursor'] is None else page([first, second])
            return {'repository': {'pullRequest': {
                'id': 'PR1', 'url': 'https://github.com/a/b/pull/1', 'headRefOid': 'abc',
                'reviewThreads': threads,
            }}}

        with patch.object(reader, 'graphql', side_effect=graphql):
            result = reader.read_threads('a', 'b', 1)

        self.assertEqual(result['head_sha'], 'abc')
        self.assertEqual([thread['id'] for thread in result['threads']], ['T1', 'T2'])
        self.assertEqual([comment['id'] for comment in result['threads'][0]['comments']], ['C1', 'C2'])
        self.assertTrue(result['threads'][1]['isResolved'])
        self.assertEqual(calls, [(reader.THREADS, None), (reader.REPLIES, 'reply-2'),
                                 (reader.THREADS, 'thread-2'), (reader.HEAD, None)])

    def test_repeated_cursor_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'did not advance'):
            list(reader.pages(lambda cursor: page([], 'stuck')))

    def test_head_change_at_readback_invalidates_entire_result(self):
        pr = {'id': 'PR1', 'url': 'https://github.com/a/b/pull/1', 'headRefOid': 'abc',
              'reviewThreads': page([])}
        with patch.object(reader, 'graphql', side_effect=[
            {'repository': {'pullRequest': pr}}, {'node': {'headRefOid': 'def'}},
        ]), self.assertRaisesRegex(ValueError, 'head changed'):
            reader.read_threads('a', 'b', 1)
