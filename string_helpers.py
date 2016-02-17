def cmp_str(str1, str2):
    """Находим общую часть в строках"""
    shared = ''
    prev_match = True
    (str1, str2) = trim_down(str1, str2)
    for i in range(0, len(str1)):
        if str1[i] == str2[i] and prev_match:
            shared += str1[i]
        else:
            prev_match = False
    return shared


def trim_down(str1, str2):
    res = ()
    if (len(str1) > len(str2)):
        res = (str1[len(str1) - len(str2):len(str2)], str2)
    elif(len(str1) < len(str2)):
        res = (str1, str2[len(str2) - len(str1):len(str2)])
    else:
        res = (str1, str2)
    return res
