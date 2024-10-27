import logging
import inspect


class CustomLogger:
    """
    CustomLogger is a wrapper around the standard Python logging module that adds a custom
    verbose logging level and includes caller information (filename, line number, class name,
    and method name) in log messages.
    Attributes:
        VERBOSE (int): Custom logging level between INFO (20) and DEBUG (10).
    Methods:
        verbose(message, *args, **kwargs):
            Logs a message with the custom verbose level, including caller information.
    """
    # Define a verbose level
    VERBOSE = 15  # Between INFO (20) and DEBUG (10)

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

        # Add a custom level if not already defined
        logging.addLevelName(self.VERBOSE, "VERBOSE")

    def verbose(self, message, *args, **kwargs):
        """Custom verbose logging method."""
        self._log_with_caller_info(self.VERBOSE, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """Passthrough info logging method."""
        self._log_with_caller_info(logging.INFO, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """Passthrough debug logging method."""
        self._log_with_caller_info(logging.DEBUG, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """Passthrough warning logging method."""
        self._log_with_caller_info(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Passthrough error logging method."""
        self._log_with_caller_info(logging.ERROR, message, *args, **kwargs)

    def _log_with_caller_info(self, level: int, message: str, *args, **kwargs):
        """Log a message with caller information."""
        # Get the calling function's frame
        frame = inspect.stack()[2]
        filename = frame.filename.split('/')[-1]  # Get the filename
        lineno = frame.lineno  # Get the line number
        method_name = frame.function  # Get the method name
        class_name = frame.frame.f_locals.get(
            'self', None).__class__.__name__ if 'self' in frame.frame.f_locals else ''  # Get the class name
        class_name = f"{class_name}." if class_name else ''

        # Log the message with the correct filename and line number
        self.logger.log(
            level, f"{filename}:{lineno} {class_name}{method_name}() - {message}", *args, **kwargs)

    @staticmethod
    def setup_logging(level: str):
        """Set up the root logger with the specified logging level."""
        log_levels = {
            'debug': logging.DEBUG,
            'verbose': CustomLogger.VERBOSE,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR
        }
        mapped_level = log_levels.get(level, logging.ERROR)
        logging.basicConfig(
            level=mapped_level,
            format='%(asctime)s %(levelname)-3.3s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
