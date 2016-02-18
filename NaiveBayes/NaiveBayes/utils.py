def get_dict_modes(dict):
    """Finds the keys of the modes of a dictionary
    @param dict: A dictionary of the form {"key":#}
    """
    highest_count = dict[max(dict)]
    modes = []
    for key in dict:
        if dict[key] == highest_count:
            modes.append(key)
    return modes

def fnv1a_64(string):
    """ Hashes a string using the 64 bit FNV1a algorithm

    For more information see:
        https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function
    @param string The key to hash
    @returns Hashed key
    """
    fnv_offset = 0xcbf29ce484222325 # The standard FNV 64 bit offset base
    fnv_prime = 0x100000001b3 # The standard FNV 64 digit prime
    hash = fnv_offset
    uint64_max = 2 ** 64
    # Iterate through the bytes of the string, ie the characters
    for char in string:
        # ord() converts the character to its unicode value
        hash = hash ^ ord(char)
        hash = (hash * fnv_prime) % uint64_max
    return hash

class NumericalDataBin():
    def __init__(self, **kwargs):
        """
        @param gte: kwarg for the minimum value it must be greater than or equal to
        @param lt: kwarg for the maximum value it must be less than
        """
        self.min = kwargs.get("gte", -float("inf"))
        self.max = kwargs.get("lt", float("inf"))

    def belongs_to_bin(self, item):
        if not isinstance(item, int) and not isinstance(item, float):
            return False
        if item >= self.max or item < self.min:
            return False
        return True

    def add_item(self, item):
        if not isinstance(item, int) and not isinstance(item, float):
            raise TypeError("NumericalDataBin is for numbers only")
        if item > self.max or item < self.min:
            raise ValueError("An item was added to the bin that is beyond the scope of the bin")
        self.values.append(item)

    def __eq__(self, other):
        if self.min == other.min and self.max == other.max:
            return True
        return False
    
    def __hash__(self):
        hash_string = str(self.min) + "," + str(self.max)
        return fnv1a_64(hash_string)