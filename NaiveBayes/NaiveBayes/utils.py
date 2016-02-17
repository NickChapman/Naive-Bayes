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