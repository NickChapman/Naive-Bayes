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
        """Determines whether a value goes into this bin"""
        if not isinstance(item, int) and not isinstance(item, float):
            return False
        if item >= self.max or item < self.min:
            return False
        return True

    def __eq__(self, other):
        """Overloaded equality
        Simply compares on range min and max
        """
        if self.min == other.min and self.max == other.max:
            return True
        return False
    
    def __hash__(self):
        """Overloaded hash operator
        Allows these data bins to be used as the keys in a dictionary
        Implements the FNV1a hashing algorithm above
        """
        hash_string = str(self.min) + "," + str(self.max)
        return fnv1a_64(hash_string)

def micro_precision(core_values, confusion_matrices):
    tp_sum = 0
    fp_sum = 0
    for core_value in core_values:
        tp_sum += confusion_matrices[core_value]["tp"]
        fp_sum += confusion_matrices[core_value]["fp"]
    return tp_sum / (tp_sum + fp_sum)

def micro_recall(core_values, confusion_matrices):
    tp_sum = 0
    fn_sum = 0
    for core_value in core_values:
        tp_sum += confusion_matrices[core_value]["tp"]
        fn_sum += confusion_matrices[core_value]["fn"]
    return tp_sum / (tp_sum + fn_sum)

def micfo_f1(core_values, confusion_matrices):
    mp = micro_precision(core_values, confusion_matrices)
    mr = micro_recall(core_values, confusion_matrices)
    return 2 * mp * mr / (mp + mr)

def macro_precision(core_values, confusion_matrices):
    precisions = []
    for core_value in core_values:
        tp = confusion_matrices[core_value]["tp"]
        fp = confusion_matrices[core_value]["fp"]
        precisions.append(tp / (tp + fp))
    return sum(precisions) / len(precisions)

def macro_recall(core_values, confusion_matrices):
    recalls = []
    for core_value in core_values:
        tp = confusion_matrices[core_value]["tp"]
        fn = confusion_matrices[core_value]["fn"]
        recalls.append(tp / (tp + fn))
    return sum(recalls) / len(recalls)

def macro_f1(core_values, confusion_matrices):
    f1s = []
    for core_value in core_values:
        tp = confusion_matrices[core_value]["tp"]
        fp = confusion_matrices[core_value]["fp"]
        fn = confusion_matrices[core_value]["fn"]
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1s.append(2 * precision * recall / (precision + recall))
    return sum(f1s) / len(f1s)

def accuracy(core_values, confusion_matrices):
    tp_sum = 0
    tn_sum = 0
    fp_sum = 0
    fn_sum = 0
    for core_value in core_values:
        tp_sum += confusion_matrices[core_value]["tp"]
        tn_sum += confusion_matrices[core_value]["tn"]
        fp_sum += confusion_matrices[core_value]["fp"]
        fn_sum += confusion_matrices[core_value]["fn"]
    return (tp_sum + tn_sum) / (tp_sum + tn_sum + fp_sum + fn_sum)