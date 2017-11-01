import unittest
import nnutils

class nnutilsTest(unittest.TestCase):
    def testMapToArrayIndex(self):
        nnutils.mapToArrayIndex([4500, 2000])

if __name__ == '__main__':
    unittest.main()
