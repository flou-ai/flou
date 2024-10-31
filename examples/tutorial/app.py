from flou.registry import registry

from part1 import BedtimeStoryWriter as BedtimeStoryWriter1
from part2 import BedtimeStoryWriter as BedtimeStoryWriter2


registry.register(BedtimeStoryWriter1)
registry.register(BedtimeStoryWriter2)

