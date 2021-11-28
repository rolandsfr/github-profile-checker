def find_index(criteria, arr):
    for i in range(0, len(arr)):
        if criteria(arr[i]):
            return i

    return None
