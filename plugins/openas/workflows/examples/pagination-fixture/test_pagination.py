import unittest

from pagination import paginate


class PaginationTests(unittest.TestCase):
    def test_one_based_pages(self):
        self.assertEqual(paginate([1, 2, 3, 4, 5], 1, 2), [1, 2])
        self.assertEqual(paginate([1, 2, 3, 4, 5], 2, 2), [3, 4])

    def test_last_and_missing_pages(self):
        self.assertEqual(paginate([1, 2, 3, 4, 5], 3, 2), [5])
        self.assertEqual(paginate([1, 2, 3], 10, 2), [])
        self.assertEqual(paginate([], 1, 2), [])

    def test_input_is_not_mutated(self):
        items = ['a', 'b', 'c']
        result = paginate(items, 1, 2)
        self.assertEqual(items, ['a', 'b', 'c'])
        self.assertIsNot(result, items)
        result.append('new')
        self.assertEqual(items, ['a', 'b', 'c'])

    def test_positive_integer_parameters(self):
        for value in (0, -1, True, False, 1.5, '2', None):
            with self.subTest(page=value):
                with self.assertRaises(ValueError):
                    paginate([1, 2, 3], value, 2)
            with self.subTest(page_size=value):
                with self.assertRaises(ValueError):
                    paginate([1, 2, 3], 1, value)


if __name__ == '__main__':
    unittest.main()
