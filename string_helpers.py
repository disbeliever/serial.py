def cmp_str(str1, str2):
    """Find common base in 2 strings, starting from string's end"""
    shared = ''
    prev_match = True
    (str1, str2) = trim_down(str1, str2)
    for i in range(0, len(str1)):
        if str1[i] == str2[i] and prev_match:
            shared += str1[i]
        else:
            prev_match = False
    return shared


def get_shared_part(str1, str2):
    """Find common base in 2 strings, starting from string's beginning"""
    prev_match = True
    shared_length = 0
    length = min(map(len, [str1, str2]))
    for i in range(0, length):
        if str1[i] == str2[i]:
            shared_length += 1
        else:
            break
    return str1[0:shared_length]


def trim_down(str1, str2):
    """Cuts shorter string to the same length as longer, cutting from the
    start"""
    res = ()
    if (len(str1) > len(str2)):
        res = (str1[len(str1) - len(str2):len(str2)], str2)
    elif(len(str1) < len(str2)):
        res = (str1, str2[len(str2) - len(str1):len(str2)])
    else:
        res = (str1, str2)
    return res
