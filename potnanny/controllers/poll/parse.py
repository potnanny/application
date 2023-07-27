import copy
import logging
from potnanny.utils import (calculate_vpd, convert_to_fahrenheit,
    flatten_list, utcnow)

logger = logging.getLogger(__name__)


class Parser:
    """
    Raw measurement parser and formatter
    """

    def __init__(self, *args, **kwargs):
        self.convert_c = False
        self.leaf_offset = -2
        self.now = utcnow()

        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


    def parse(self, data: list) -> list:
        """
        Parse raw bulk measurement data from all devices in to a list of
        individual formatted measurements.

        args:
            - list
        returns:
            - list
        """

        results = []
        clean = flatten_list(data)
        for c in clean:
            results += self._extract(c)

        for m in results:
            m['created'] = self.now

        return results


    def _extract(self, data: dict) -> list:
        """
        Extract list of individual measurements from device polled data

        args:
            - dict (meas data from a device)
        returns:
            - list [
                {device_id: 1, type: temperature, value: 24.1},
                {device_id: 1, type: humidity, value: 55.1},
            ]
        """

        measurements = []
        if data is None:
            logger.debug("received None instead of a dict?")
            return []

        try:
            data['device_id'] = data.pop('id')
            values = data.pop('values')

            # vpd calcs are done first
            if 'temperature' in values and 'humidity' in values:
                try:
                    m = copy.copy(data)
                    t = values['temperature'] + self.leaf_offset
                    h = values['humidity']
                    m.update({
                        'type': 'vpd',
                        'value': calculate_vpd(t, h) })
                    measurements.append(m)
                except Exception as x:
                    logger.warning(x)

            for key, value in values.items():
                m = copy.copy(data)

                if key == 'temperature' and self.convert_c is True:
                    value = convert_to_fahrenheit(value)

                m.update({'type': key, 'value': value, 'created': self.now})
                measurements.append(m)

        except Exception as x:
            logger.warning(x)

        return measurements
