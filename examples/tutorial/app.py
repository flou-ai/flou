from flou.registry import registry

from part1 import BedtimeStoryWriter as BedtimeStoryWriter1
from part2 import BedtimeStoryWriter as BedtimeStoryWriter2
from part3 import BedtimeStoryWriter as BedtimeStoryWriter3
from riudor1 import AIPublisher as AIPublisher


registry.register(BedtimeStoryWriter1)
registry.register(BedtimeStoryWriter2)
registry.register(BedtimeStoryWriter3)
registry.register(AIPublisher)
