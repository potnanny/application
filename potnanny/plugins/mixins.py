import re
import logging


logger = logging.getLogger(__name__)


class FingerprintMixin:
    """
    This is a class mixin for BLE plugins, to be able to recognize a
    BLE device that can be communicated with (by its device address or name)

    Each entry in a class fingerprint definition must match, in order for
    this to return True.
    """

    @classmethod
    def recognize_this(cls, fp):
        if not hasattr(cls, 'fingerprint'):
            logger.warning("Class %s no fingerprint defined" % cls)
            return False

        for key, regex in cls.fingerprint.items():
            if key not in fp:
                return False

            if not regex.search(fp[key]):
                return False

        return True
