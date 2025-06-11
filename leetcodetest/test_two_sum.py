from leetcodetest.two_sum import Solution

# leetcode two sum
def test_two_sum():
    sol = Solution()
    assert sol.twoSum([2, 7, 11, 15], 9) == [0, 1]
    assert sol.twoSum([3, 2, 4], 6) == [1, 2]
    assert sol.twoSum([3, 3], 6) == [0, 1]
    print("All tests passed.")

if __name__ == "__main__":
    test_two_sum()
