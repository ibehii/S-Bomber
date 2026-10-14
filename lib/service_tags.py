# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Service categorization, tagging dictionary, and query filters."""

from typing import Final

SERVICE_TAGS_MAP: Final[dict[str, list[str]]] = {
    "transport": [
        "tapsi_passenger",
        "tapsi_biker",
        "tapsi_driver",
        "snapp_app_link",
        "snapp_login_page",
        "snapp_worker_login_page",
        "snapp_trip",
        "itoll",
        "itoll_app_link",
        "hamrah_mechanic",
    ],
    "marketplace": [
        "divar",
        "sheypoor",
        "sheypoor_app_link",
        "basalam",
        "pindo",
        "buskool",
        "digikala",
        "trob",
    ],
    "food": [
        "snapp_food",
        "snapp_market",
    ],
    "entertainment": [
        "filimo",
        "FilmNet",
        "GapFilm",
        "telewebion",
        "varzesh3",
    ],
    "medical": [
        "drsaina",
        "DrDr",
        "nobat",
        "mihanpezeshk_patients",
        "mihanpezeshk_doctor",
    ],
    "fintech": [
        "lendo",
        "azki",
        "bimito",
    ],
    "education": [
        "classino",
        "Nashr_olgoo",
    ],
    "ecommerce": [
        "banimode",
        "alibaba",
        "okcs",
        "oketab",
        "see5",
        "sibirani",
        "goftino",
        "pooleno",
        "anar360",
    ],
}


def get_available_tags() -> list[str]:
    """Return sorted list of all available service category tags."""
    return sorted(SERVICE_TAGS_MAP.keys())


def get_services_by_tags(tags: list[str] | str) -> list[str]:
    """Retrieve unique service names matching one or more category tags.

    Parameters
    ----------
    tags : list[str] | str
        Single tag string, comma-separated tag string, or list of tag strings.

    Returns
    -------
    list[str]
        Deduplicated, sorted list of service names belonging to specified tags.
    """
    if isinstance(tags, str):
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
    else:
        tag_list = [t.strip().lower() for t in tags if t.strip()]

    matched_services: set[str] = set()
    for tag_name in tag_list:
        if tag_name in SERVICE_TAGS_MAP:
            matched_services.update(SERVICE_TAGS_MAP[tag_name])

    return sorted(matched_services)


__all__ = [
    "SERVICE_TAGS_MAP",
    "get_available_tags",
    "get_services_by_tags",
]
