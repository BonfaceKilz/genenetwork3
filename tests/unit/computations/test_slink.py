"""Module contains tests for slink"""
import unittest
from unittest import TestCase

from gn3.computations.slink import nearest
from gn3.computations.slink import LengthError
from gn3.computations.slink import MirrorError

class TestSlink(TestCase):
    """Class for testing slink functions"""

    def test_nearest_expects_list_of_lists(self):
        # This might be better handled with type-hints and mypy
        for item in [9, "some string", 5.432,
                     [1,2,3], ["test", 7.4]]:
            with self.subTest(item=item):
                with self.assertRaises(ValueError, msg="Expected list or tuple"):
                    nearest(item, 1, 1)

    def test_nearest_does_not_allow_empty_lists(self):
        for lst in [[],
                    [[],[]],
                    [[],[],[]],
                    [[0, 1, 2],[],[1, 2, 0]]]:
            with self.subTest(lst=lst):
                with self.assertRaises(ValueError):
                    nearest(lst, 1, 1)

    def test_nearest_expects_exception_if_all_child_lists_are_not_of_equal_length_to_length_of_parent_list(self):
        for lst in [[[0,1]],
                    [[0,1,2],[3,4,5]],
                    [[0,1,2,3],[4,5,6],[7,8,9,0]],
                    [[0,1,2,3,4],[5,6,7,8,9],[1,2,3,4,5],[2,3],[3,4,5,6,7]]]:
            with self.subTest(lst=lst):
                with self.assertRaises(LengthError):
                    nearest(lst, 1, 1)

    def test_nearest_expects_exception_if_distance_of_child_from_itself_is_not_zero(self):
        for lst in [[[1]],
                    [[1,2],[3,4]],
                    [1,0,0],[0,0,5],[0,3,4],
                    [0,0,0,0],[0,0,3,3],[0,1,2,3],[0,3,2,0]]:
            with self.subTest(lst=lst):
                with self.assertRaises(ValueError):
                    nearest(lst, 1, 1)

    def test_nearest_expects_exception_if_distance_from_child_a_to_child_b_is_not_distance_from_child_b_to_child_a(self):
        for lst in [[[0,1],[2,0]],
                    [[0,1,2],[1,0,3],[9,7,0]],
                    [[0,1,2,3],[7,0,2,3],[2,3,0,1],[8,9,5,0]]]:
            with self.subTest(lst=lst):
                with self.assertRaises(MirrorError):
                    nearest(lst, 1, 1)

    def test_nearest_expects_zero_or_positive_distances(self):
        # Based on:
        # https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/slink.py#L87-L89
        for lst in [[[0,-1,2,3],[-1,0,3,4],[2,3,0,5],[3,4,5,0]],
                    [[0,1,-2,3],[1,0,3,4],[-2,3,0,5],[3,4,5,0]],
                    [[0,1,2,3],[1,0,-3,4],[2,-3,0,5],[3,4,5,0]],
                    [[0,1,2,-3],[1,0,3,4],[2,3,0,5],[-3,4,5,0]],
                    [[0,1,2,3],[1,0,3,-4],[2,3,0,5],[3,-4,5,0]],
                    [[0,1,2,3],[1,0,3,4],[2,3,0,-5],[3,4,-5,0]]]:
            with self.subTest(lst=lst):
                with self.assertRaises(ValueError, msg="Distances should be positive."):
                    nearest(lst, 1, 1)

    def test_nearest_with_expected(self):
        # Give this test a better name
        # The lists in this tests are taken from:
        # https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/slink.py#L39-L40
        for lst, i, j, expected in [[[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     0,0,0],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     0,1,9],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     0,2,3],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     0,3,6],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     0,4,11],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     1,0,9],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     1,1,0],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     1,2,7],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     1,3,5],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     1,4,10],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     2,0,3],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     2,1,7],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     2,2,0],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     2,3,9],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     2,4,2],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     3,0,6],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     3,1,5],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     3,2,9],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     3,3,0],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     3,4,8],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     4,0,11],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     4,1,10],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     4,2,2],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     4,3,8],
                                    [[[0,9,3,6,11],[9,0,7,5,10],[3,7,0,9,2],[6,5,9,0,8],[11,10,2,8,0]],
                                     4,4,0],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     0,0,0],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     0,1,9],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     0,2,5.5],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     0,3,6],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     0,4,11],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     1,0,9],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     1,1,0],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     1,2,7],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     1,3,5],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     1,4,10],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     2,0,5.5],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     2,1,7],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     2,2,0],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     2,3,9],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     2,4,2],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     3,0,6],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     3,1,5],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     3,2,9],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     3,3,0],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     3,4,3],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     4,0,11],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     4,1,10],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     4,2,2],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     4,3,3],
                                    [[[0,9,5.5,6,11],[9,0,7,5,10],[5.5,7,0,9,2],[6,5,9,0,3],[11,10,2,3,0]],
                                     4,4,0]]:
            with self.subTest(lst=lst):
                self.assertEqual(nearest(lst, i, j), expected)
