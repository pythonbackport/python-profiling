# Backport from python 3.15's new library 'profiling'

import locale


def fmt(value: int | float, decimals: int = 1) -> str:
    return locale.format_string(f'%.{decimals}f', value, grouping=True)