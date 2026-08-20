import matplotlib.pyplot as plt


def show_nonblocking():
    """Display open figures without blocking, pumping the GUI event loop once.

    plt.show(block=False) creates the window but never renders it, because the
    caller immediately blocks on input(). The short pause lets the backend draw.
    """
    plt.show(block=False)
    plt.pause(0.1)


def close_figure(fig):
    """Close a figure, tolerating a window the user already closed by hand.

    While a non-blocking figure is up the Tk event loop is not running, so a
    manual close leaves the manager registered with its Tcl commands already
    deleted. Closing it then raises TclError, which otherwise surfaces as a
    crash from matplotlib's atexit handler at interpreter shutdown.
    """
    if fig is None:
        return
    try:
        plt.close(fig)
    except Exception:
        # Teardown only - the window is gone either way, nothing left to salvage.
        pass
