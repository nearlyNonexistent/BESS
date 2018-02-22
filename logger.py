"""Logger for BESS."""
# First Party Imports
import logging
# Third Party Imports
import attr


@attr.s
class Logger():
    """Handles logging."""

    logfile = attr.ib()
    debug = attr.ib()
    loglevel = attr.ib()

    def __attrs_post_init__(self):
        """Initialization."""
        # File logger
        if self.debug:
            loglevel_root = logging.DEBUG
        else:
            loglevel_root = logging.INFO
        root_logger = logging.getLogger()
        root_logger.setLevel(loglevel_root)
        handler = logging.FileHandler(self.logfile, 'w', 'utf-8')
        handler.setFormatter(logging.Formatter(("%(asctime)s: %(levelname)s:"
                                                "%(name)s: %(message)s")))
        root_logger.addHandler(handler)

        # Logger for console.
        console = logging.StreamHandler()
        if self.loglevel == "q":
            self.loglevel = logging.ERROR
        elif self.loglevel == "v":
            self.loglevel = logging.INFO
        else:
            self.loglevel = logging.WARNING
        console.setLevel(self.loglevel)
        console.setFormatter(logging.Formatter(
                             "%(name)-15s: %(levelname)-7s: %(message)s"))
        logging.getLogger("").addHandler(console)

    def abbr_log(self, minimal, full):
        """Log minimal when not set to VERBOSE, otherwise log full."""
        if self.loglevel > logging.INFO:
            print(minimal)
        else:
            logging.info(full)
