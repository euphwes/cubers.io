""" Utilities for paginating events records pages """
from collections import namedtuple
from flask import url_for


def _build_pagination(page, event_name):
    """ Builds necessary information to render pagination component on templates """
    
    prev_url = url_for("event_results", event_name=event_name, page=page.prev_num) if page.has_prev else None
    next_url = url_for("event_results", event_name=event_name, page=page.next_num) if page.has_next else None
    
    pagination = {
        "prev_url": prev_url,
        "next_url": next_url,
        "buttons_content": _build_page_links(page.page, page.pages),
    }

    return pagination


def _build_page_links(current_page ,n_pages):
    """ Generates page links omitting intermediate page buttons to always 
    have a maximum of 5 page link buttons and 2 ellipsis inactive buttons.
    For an event record with 20 pages, at page 15, it'll look like this:
    [1][...][14][15][16][...][20] """

    PaginationLinks = namedtuple('PaginationLinks', ['text', 'url'])

    if n_pages < 6:
        return [
            PaginationLinks(
                str(n),
                url_for("event_results", event_name=event_name, page=n)
            )
            for n in range(1, n_pages)
        ]
    
    else:
        links = []

        # first page
        links.append(
            PaginationLinks(
                "1",
                url_for("event_results", event_name=event_name, page=1)
            )
        )

        # first ellipsis button content
        links.append(PaginationLinks("...", "#"))
        
        # 3 middle pages
        middle = n_pages // 2
        for n in range(middle-1, middle+2):
            links.append(
                PaginationLinks(
                    str(n),
                    url_for("event_results", event_name=event_name, page=n)
                )
            )

        # second ellipsis button content
        links.append(PaginationLinks("...", "#"))

        # last page
        links.append(
            PaginationLinks(
                str(n_pages),
                url_for("event_results", event_name=event_name, page=n_pages)
            )
        )
        return links
