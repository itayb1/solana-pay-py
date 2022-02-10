from typing import Union

def is_null(val: object) -> bool:
    if val == None or val == "None":
        return True
    return False

def find_decimals(val: Union[float, int]):
    num_of_decimals = str(val)[::-1].find('.')
    if num_of_decimals <= 0:
        return 0
        
    return num_of_decimals