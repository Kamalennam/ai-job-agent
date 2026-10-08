import math


def analysis_progress(received_chars: int) -> int:
    """Map streamed parser output to the 35–90 band.

    The bar moves as characters arrive and levels off before the save step.
    """
    if received_chars <= 0:
        return 35
    fraction = 1 - math.exp(-received_chars / 700)
    return min(90, 35 + int(55 * fraction))
