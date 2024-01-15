def search_in_dict_values(dictionary: dict, target: str) -> str | None:
    for key, values in dictionary.items():
        if target in values:
            return key
