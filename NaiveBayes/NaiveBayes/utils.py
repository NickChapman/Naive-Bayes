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

class NumericalDataBin():
    def __init__(self, **kwargs):
        """
        @param gte: kwarg for the minimum value it must be greater than or equal to
        @param lt: kwarg for the maximum value it must be less than
        """
        self.min = kwargs.get("gte", -float("inf"))
        self.max = kwargs.get("lt", float("inf"))

    def belongs_to_bin(self, item):
        if not isinstance(item, int) or not isinstance(item, float):
            return False
        if item > self.max or item < self.min:
            return False
        return True

    def add_item(self, item):
        if not isinstance(item, int) or not isinstance(item, float):
            raise TypeError("NumericalDataBin is for numbers only")
        if item > self.max or item < self.min:
            raise ValueError("An item was added to the bin that is beyond the scope of the bin")
        self.values.append(item)

    