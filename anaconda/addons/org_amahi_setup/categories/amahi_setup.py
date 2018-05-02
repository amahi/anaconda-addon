



from pyanaconda.ui.categories import SpokeCategory

__all__ = ["AmahiCategory"]

N_ = lambda x: x


class AmahiCategory(SpokeCategory):
    """
    Class for the Amahi category. Category groups related spokes
    together. Both logically and visually (creates a box on a hub). It
    references a class of the hub it is supposed to be placed on. On the
    other hand spokes reference a class of the category they should be
    included in.

    """

    displayOnHubGUI = "SummaryHub"
    displayOnHubTUI = "SummaryHub"
    title = N_("AMAHI SERVER SETUP")
