'''
    Little helpful utility functions.
'''


def is_ip(string):
    '''
        Return True if string is a valid ip address, False otherwise.
    '''
    try:
        nums = [int(s) for s in string.split(".")]
    except ValueError:
        return False
    return len(nums) == 4 and all(0 <= n < 256 for n in nums)
