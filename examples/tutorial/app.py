from flou.registry import registry

from part1 import BedtimeStoryWriter as BedtimeStoryWriter1
from part2 import BedtimeStoryWriter as BedtimeStoryWriter2
from part3 import BedtimeStoryWriter as BedtimeStoryWriter3
from part4 import BedtimeStoryWriter as BedtimeStoryWriter4
from riudor1 import AIPublisher as AIPublisher


registry.register(BedtimeStoryWriter1)
registry.register(BedtimeStoryWriter2)
registry.register(BedtimeStoryWriter3)
registry.register(BedtimeStoryWriter4)
registry.register(AIPublisher)
