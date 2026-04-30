"""Doc2Test mutation tool — 4 operators (ER / AM / SLI / EHD).

Generates 30 unique mutated programs per OSS subject (150 total) and
records the corresponding entries for the runtime-injected industrial
mutants (30 more, NDA-redacted; cf. paper §4.4).
"""
from .operators import ELEMENT_REMOVAL, ATTRIBUTE_MODIFICATION, STATE_LOGIC_INVERSION, EVENT_HANDLER_DETACHMENT, OPERATORS

__all__ = ["ELEMENT_REMOVAL", "ATTRIBUTE_MODIFICATION", "STATE_LOGIC_INVERSION", "EVENT_HANDLER_DETACHMENT", "OPERATORS"]
