from __future__ import annotations

from typing import Optional, Sequence

from htmltools import (
    MetadataNode,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagList,
    css,
    tags,
)

from ..._typing_extensions import Literal
from ...types import MISSING, MISSING_TYPE, NavSetArg
from ...ui import page_bootstrap
from ...ui._utils import get_window_title
from ._css_unit import CssUnit, validate_css_padding, validate_css_unit
from ._fill import as_fillable_container
from ._navs import navset_bar
from ._sidebar import Sidebar
from ._utils import consolidate_attrs


def page_navbar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: Optional[str | Tag | TagList] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    # Only page_navbar gets enhancedtreatement for `fillable`
    # If an `*args`'s `data-value` attr string is in `fillable`, then the component is fillable
    fillable: bool | list[str] = False,
    fill_mobile: bool = False,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    bg: Optional[str] = None,
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
) -> Tag:
    """
    Create a page with a navbar and a title.

    Parameters
    ----------

    args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    position
        Determines whether the navbar should be displayed at the top of the page with
        normal scrolling behavior ("static-top"), pinned at the top ("fixed-top"), or
        pinned at the bottom ("fixed-bottom"). Note that using "fixed-top" or
        "fixed-bottom" will cause the navbar to overlay your body content, unless you
        add padding (e.g., ``tags.style("body {padding-top: 70px;}")``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    bg
        Background color of the navbar (a CSS color).
    inverse
        Either ``True`` for a light text color or ``False`` for a dark text color.
    collapsible
        ``True`` to automatically collapse the navigation elements into a menu when the
        width of the browser is less than 940 pixels (useful for viewing on smaller
        touchscreen device)
    fluid
        ``True`` to use fluid layout; ``False`` to use fixed layout.
    window_title
        The browser's window title (defaults to the host URL of the page). Can also be
        set as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.nav`
    :func:`~shiny.ui.nav_menu`
    :func:`~shiny.ui.navset_bar`
    :func:`~shiny.ui.page_fluid`

    Example
    -------
    See :func:`~shiny.ui.nav`.
    """
    if sidebar is not None and not isinstance(sidebar, Sidebar):
        raise TypeError(
            "`sidebar=` is not a `Sidebar` instance. Use `ui.sidebar(...)` to create one."
        )

    # If a sidebar is provided, we want the layout_sidebar(fill = TRUE) component
    # (which is a sibling of the <nav>) to always fill the page
    if fillable is False and sidebar is None:
        # `page_func = page_bootstrap` throws type errors. Wrap in a function to get around them
        def page_func(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
            return page_bootstrap(*args, **kwargs)

    else:

        def page_func(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
            return page_fillable(
                *args,
                fill_mobile=fill_mobile,
                padding=0,
                gap=0,
                **kwargs,
            )

    return page_func(
        navset_bar(
            *args,
            title=title,
            id=id,
            selected=selected,
            sidebar=sidebar,
            fillable=fillable,
            position=position,
            header=header,
            footer=footer,
            bg=bg,
            inverse=inverse,
            collapsible=collapsible,
            fluid=fluid,
        ),
        get_window_title(title, window_title=window_title),
        title=None,
        # theme = theme,
        lang=lang,
    )


def page_fillable(
    *args: TagChild | TagAttrs,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    gap: Optional[CssUnit] = None,
    fill_mobile: bool = False,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    attrs, children = consolidate_attrs(*args, **kwargs)

    style = css(
        padding=validate_css_padding(padding),
        gap=validate_css_unit(gap),
        __bslib_page_fill_mobile_height="100%" if fill_mobile else "auto",
    )

    return page_bootstrap(
        tags.head(tags.style("html { height: 100%; }")),
        as_fillable_container(
            tags.body(
                {"class": "bslib-page-fill", "style": style},
                attrs,
                *children,
            ),
        ),
        title=title,
        lang=lang,
    )
