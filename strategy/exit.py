from config import (
    STOP_LOSS_PERCENT,
    DEATH_CROSS_CONFIRMATION,
)


def get_exit_signal(
    state,
    current_return,
    gap_ratio,
):
    """
    Returns the exit reason or None.

    Exit Priority

    1. Stop Loss
    2. Gap + EMA Confirmation
    3. Confirmed Death Cross
    """

    # -----------------------------------------
    # Stop Loss
    # -----------------------------------------

    if current_return <= STOP_LOSS_PERCENT:

        return "Stop Loss"

    # -----------------------------------------
    # Gap + EMA Confirmation
    # -----------------------------------------

    if (
        state["bearish_seen"]
        and
        state["gap_seen"]
    ):

        return "Gap + EMA Confirmation"

    # -----------------------------------------
    # Confirmed Death Cross
    # -----------------------------------------

    if (
        state["death_seen"]
        and
        gap_ratio <= DEATH_CROSS_CONFIRMATION
    ):

        return "Confirmed Death Cross"

    return None