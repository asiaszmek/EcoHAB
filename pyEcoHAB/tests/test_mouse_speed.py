from __future__ import print_function, division, absolute_import
from pyEcoHAB import mouse_speed as ms
import unittest

try:
    basestring
except NameError:
    basestring = str


class TestExtractDirections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        antennas1 = [1, 2,   3, 4,  5,  6,  7,   8,  1, 2]
        times1 = [15, 16.5, 19, 20, 21, 22, 24, 25, 29, 34 ]
        antennas2 = [8, 1,   2,    1,  2,  3,  4,   5, 6,   7,   8]
        times2 =   [10, 16, 19, 19.5, 22, 25,  26, 27, 28, 31, 35]
        cls.res1 = ms.extract_directions(times1, antennas1)
        cls.res2 = ms.extract_directions(times2, antennas2)

    def test_1(self):
        direction_dict = {key:[[], []] for key in ms.keys}
        direction_dict["12"][0].append(15)
        direction_dict["12"][1].append(16.5)
        direction_dict["34"][0].append(19)
        direction_dict["34"][1].append(20)
        direction_dict["56"][0].append(21)
        direction_dict["56"][1].append(22)
        direction_dict["78"][0].append(24)
        direction_dict["78"][1].append(25)
        direction_dict["12"][0].append(29)
        direction_dict["12"][1].append(34)
        
        self.assertEqual(direction_dict, self.res1)

    def test_2(self):
        direction_dict = {key:[[], []] for key in ms.keys}
        direction_dict["12"][0].append(19.5)
        direction_dict["12"][1].append(22)
        direction_dict["34"][0].append(25)
        direction_dict["34"][1].append(26)
        direction_dict["56"][0].append(27)
        direction_dict["56"][1].append(28)
        direction_dict["78"][0].append(31)
        direction_dict["78"][1].append(35)
        
        self.assertEqual(direction_dict, self.res2)


class TestFollowing2ndMouseInPipe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        antennas1 = [1, 2]
        times1 = [15, 16.5]
        antennas2 = [8, 1, 2, 3, 4, 5]
        times2 = [10, 16, 19, 19.5, 22, 25]
        dir1 = ms.extract_directions(times1, antennas1)
        dir2 = ms.extract_directions(times2, antennas2)
        res = ms.following_single_pair(dir1, dir2)
        cls.out1, cls.time_together1, cls.intervals1= res

        antennas1 = [1, 2, 3, 4, 5]
        times1 = [15, 16.5, 19, 20, 21]
        antennas2 = [8, 1, 2, 3, 4, 5]
        times2 = [10, 16, 19, 19.5, 22, 25]
        dir1 = ms.extract_directions(times1, antennas1)
        dir2 = ms.extract_directions(times2, antennas2)
        res = ms.following_single_pair(dir2, dir1)
        cls.out2, cls.time_together2, cls.intervals2 = res

        antennas1 = [1, 2,   3, 4,  5,  6,  7,   8,  1, 2]
        times1 = [15, 16.5, 19, 20, 21, 22, 24, 25, 29, 34 ]
        antennas2 = [8, 1,   2,    3,  4,  5,  6,   7, 8,   1,   2]
        times2 =   [10, 16, 19, 19.5, 22, 25,  26, 27, 28, 31, 35]
        dir1 = ms.extract_directions(times1, antennas1)
        dir2 = ms.extract_directions(times2, antennas2)
        res = ms.following_single_pair(dir1, dir2)
        cls.out3, cls.time_together3, cls.intervals3 = res

    def test_following_11(self):
        self.assertEqual(self.out1, 1)

    def test_following_12(self):
        self.assertEqual(self.time_together1, 0.5)

    def test_following_13(self):
        self.assertEqual(self.intervals1, [4])

    def test_not_following_more_1(self):
        self.assertEqual(self.out2, 0)

    def test_not_following_more_2(self):
        self.assertEqual(self.time_together2, 0)

    def test_not_following_more_3(self):
        self.assertEqual(self.intervals2, [])

    def test_following_31(self):
        self.assertEqual(self.out3, 3)

    def test_following_32(self):
        self.assertEqual(self.time_together3, 4)

    def test_following_33(self):
        self.assertEqual(self.intervals3, [4, 6, 3])


class TestFollowingMatrices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ta = {"mouse1": [[15, 16.5, 19, 20, 21, 22, 24, 25, 29, 34 ],
                         [1, 2,   3,    4,  5,  6,  7,   8,  1, 2]],
              "mouse2": [[10, 16, 19, 19.5, 22, 25,  26, 27, 28, 31, 35],
                         [8, 1,   2,    3,  4,  5,  6,   7, 8,   1,   2],],
              "mouse3": [[10, 16, 17, 18, 22, 25, 26, 27],
                         [1,  2,   3, 4,  4,  3,  2, 1],]
        }
        mice_list = ["mouse1", "mouse2", "mouse3"]
        directions_dict = {}
        for mouse in mice_list:
            directions_dict[mouse] = ms.extract_directions(*ta[mouse])
        out = ms.following_matrices(directions_dict,
                                    mice_list,
                                    0, 1000)
        cls.following = out[0]
        cls.time_together = out[1]
        cls.interval_details = out[2]

    def test_following_diag_1(self):
        self.assertEqual(self.following[0, 0], 0)

    def test_following_diag_2(self):
        self.assertEqual(self.following[1, 1], 0)

    def test_following_diag_3(self):
        self.assertEqual(self.following[2, 2], 0)

    def test_following_0_1(self):
        self.assertEqual(self.following[0, 1], 3)

    def test_following_0_2(self):
        self.assertEqual(self.following[0, 2], 0)

    def test_following_1_0(self):
        self.assertEqual(self.following[1, 0], 0)

    def test_following_1_2(self):
        self.assertEqual(self.following[1, 2], 0)

    def test_following_2_0(self):
        self.assertEqual(self.following[2, 0], 1)

    def test_following_2_1(self):
        self.assertEqual(self.following[2, 1], 0)

    def test_time_together_diag_0(self):
        self.assertEqual(self.time_together[0, 0], 0)

    def test_time_together_diag_1(self):
        self.assertEqual(self.time_together[1, 1], 0)

    def test_time_together_diag_2(self):
        self.assertEqual(self.time_together[2, 2], 0)

    def test_time_together_0_1(self):
        self.assertEqual(self.time_together[0, 1], 0.004)

    def test_time_together_0_2(self):
        self.assertEqual(self.time_together[0, 2], 0)

    def test_time_together_1_0(self):
        self.assertEqual(self.time_together[1, 0], 0)

    def test_time_together_1_2(self):
        self.assertEqual(self.time_together[1, 2], 0)

    def test_time_together_2_0(self):
        self.assertEqual(self.time_together[2, 0], 0.001)

    def test_time_together_2_1(self):
        self.assertEqual(self.time_together[2, 1], 0)

    def test_interval_details_empty(self):
        self.assertEqual(self.time_together[2, 1], 0)

if __name__ == '__main__':
    unittest.main()
