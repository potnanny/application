import asyncio
import copy
import logging
from potnanny.plugins import PipelinePlugin

logger = logging.getLogger(__name__)


class Pipeline:
    """
    All new measurements go into the pipline and delivered to targets
    """

    def __init__(self, *args, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


    async def input(self, measurements):
        """
        Input measurements into the pipeline for processing
        """

        tasks = []
        for p in PipelinePlugin.plugins:
            logger.debug("Queueing pipeline job: %s" % p)
            tasks.append(p().input(copy.deepcopy(measurements)))

        if not tasks:
            return

        try:
            await asyncio.gather(*tasks)
        except Exception as x:
            logger.warning(x)
