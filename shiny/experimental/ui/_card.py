from __future__ import annotations

import base64
import io
import mimetypes
from pathlib import Path, PurePath
from typing import Optional

from htmltools import (
    HTML,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    Tagifiable,
    TagList,
    css,
    div,
    tags,
)

from ..._typing_extensions import Literal, Protocol
from ...types import MISSING, MISSING_TYPE
from ._css_unit import CssUnit, validate_css_unit
from ._fill import as_fill_carrier, bind_fill_role
from ._htmldeps import card_dependency
from ._utils import consolidate_attrs

__all__ = (
    "CardItem",
    "card",
    "card_body",
    "card_title",
    "card_header",
    "card_footer",
    "card_image",
)


# TODO-maindocs; @add_example()
def card(
    *args: TagChild | TagAttrs | CardItem,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    wrapper: WrapperCallable | None | MISSING_TYPE = MISSING,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    A Bootstrap card component

    A general purpose container for grouping related UI elements together with a border
    and optional padding. To learn more about `card()`s, see [this
    article](https://rstudio.github.io/bslib/articles/cards.html).

    Parameters
    ----------
    *args
        Unnamed arguments can be any valid child of an [htmltools tag][htmltools::tags]
        (which includes card items such as :func:`~shiny.experimental.ui.card_body()`.
        Named arguments become HTML attributes on the returned Tag.
    full_screen
        If `True`, an icon will appear when hovering over the card body. Clicking the
        icon expands the card to fit viewport size.
    height,max_height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen` (in this case, consider setting a `height` in
        :func:`~shiny.experimental.ui.card_body()`).
    fill
        Whether or not to allow the card to grow/shrink to fit a fillable container with
        an opinionated height (e.g., :func:`~shiny.experimental.ui.page_fillable()`).
    class_
        Additional CSS classes for the returned Tag.
    wrapper
        A function (which returns a UI element) to call on unnamed
      arguments in `*args` which are not already card item(s) (like
      :func:`~shiny.experimental.ui.card_header()`,
      :func:`~shiny.experimental.ui.card_body()`, etc.). Note that non-card items are
      grouped together into one `wrapper` call (e.g. given
      `card("a", "b", card_body("c"), "d")`, `wrapper` would be called twice,
      once with `"a"` and `"b"` and once with `"d"`).

    Returns
    -------
    :
        A [htmltools::div()] tag.

    See Also
    --------
    * :func:`~shiny.experimental.ui.navs_tab_card()` for cards with multiple tabs.
    * :func:`~shiny.experimental.ui.layout_column_wrap()` for laying out multiple cards
      (or multiple columns inside a card).
    * :func:`~shiny.experimental.ui.card_header()` for creating a header within the card.
    * :func:`~shiny.experimental.ui.card_title()` for creating a title within the card body.
    * :func:`~shiny.experimental.ui.card_body()` for putting content inside the card.
    * :func:`~shiny.experimental.ui.card_footer()` for creating a footer within the card.
    * :func:`~shiny.experimental.ui.card_image()` for adding an image to the card.
    """
    if isinstance(wrapper, MISSING_TYPE):
        wrapper = card_body

    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)
    children = _wrap_children_in_card(*children, wrapper=wrapper)

    tag = div(
        {
            "class": "card bslib-card",
            "style": css(
                height=validate_css_unit(height),
                max_height=validate_css_unit(max_height),
            ),
            "data-bslib-card-init": True,
        },
        *children,
        attrs,
        _full_screen_toggle() if full_screen else None,
        card_dependency(),
        _card_js_init(),
    )

    return bind_fill_role(tag, container=True, item=fill)


def _card_js_init() -> Tag:
    return tags.script(
        {"data-bslib-card-init": True},
        "window.bslib.Card.initializeAllCards();",
    )


def _full_screen_toggle() -> Tag:
    return tags.span(
        {
            "class": "bslib-full-screen-enter badge rounded-pill bg-dark",
            "data-bs-toggle": "tooltip",
            "data-bs-placement": "bottom",
            "title": "Expand",
        },
        _full_screen_toggle_icon(),
    )


# via bsicons::bs_icon("arrows-fullscreen")
def _full_screen_toggle_icon() -> HTML:
    return HTML(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-arrows-fullscreen " style="height:1em;width:1em;fill:currentColor;" aria-hidden="true" role="img" ><path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707zm4.344 0a.5.5 0 0 1 .707 0l4.096 4.096V11.5a.5.5 0 1 1 1 0v3.975a.5.5 0 0 1-.5.5H11.5a.5.5 0 0 1 0-1h2.768l-4.096-4.096a.5.5 0 0 1 0-.707zm0-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707zm-4.344 0a.5.5 0 0 1-.707 0L1.025 1.732V4.5a.5.5 0 0 1-1 0V.525a.5.5 0 0 1 .5-.5H4.5a.5.5 0 0 1 0 1H1.732l4.096 4.096a.5.5 0 0 1 0 .707z"></path></svg>'
    )


############################################################################


class CardItem:
    # TODO-barret; document
    def __init__(
        self,
        x: TagChild,
    ):
        self._x = x

    def resolve(self) -> TagChild:
        return self._x

    def tagify(self) -> TagList:
        return TagList(self._x).tagify()


# TODO-maindocs; @add_example()
def card_body(
    *args: TagChild | TagAttrs,
    fillable: bool = True,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    max_height_full_screen: Optional[CssUnit] | MISSING_TYPE = MISSING,
    height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> CardItem:
    # For a general overview of the [card()] API, see [this article](https://rstudio.github.io/bslib/articles/cards.html).
    """
    Card body container

    A general container for the "main content" of a [card()]. This component is designed
    to be provided as direct children to :func:`~shiny.experimental.ui.card()`.

    Parameters
    ----------
    *args
        Contents to the card's body. Or tag attributes that are supplied to the
        resolved `Tag` object.
    fillable
        Whether or not the card item should be a fillable (i.e. flexbox) container.
    min_height,max_height,max_height_full_screen
        Any valid CSS length unit. If `max_height_full_screen` is missing, it is set to
        `max_height`.
    height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen` (in this case, consider setting a `height` in
        :func:`~shiny.experimental.ui.card_body()`).
    gap
        A CSS length unit defining the `gap` (i.e., spacing) between elements provided
        to `*args`. This argument is only applicable when `fillable = TRUE`.
    fill
        Whether to allow this element to grow/shrink to fit its `card()` container.
    class_
        Additional CSS classes for the returned Tag.
    **kwargs
        Additional HTML attributes for the returned Tag.

    Returns
    -------
    :
        A `~shiny.experiemental.ui.CardItem` object.

    See Also
    --------
    * :func:`~shiny.experimental.ui.navs_tab_card()` for cards with multiple tabs.
    * :func:`~shiny.experimental.ui.layout_column_wrap()` for laying out multiple cards
        (or multiple columns inside a card).
    * :func:`~shiny.experimental.ui.card()` for creating a card component.
    * :func:`~shiny.experimental.ui.card_header()` for creating a header within the card.
    * :func:`~shiny.experimental.ui.card_title()` for creating a title within the card body.
    * :func:`~shiny.experimental.ui.card_footer()` for creating a footer within the card.
    * :func:`~shiny.experimental.ui.card_image()` for adding an image to the card.
    """
    if isinstance(max_height_full_screen, MISSING_TYPE):
        max_height_full_screen = max_height

    div_style_args = {
        "min-height": validate_css_unit(min_height),
        "--bslib-card-body-max-height": validate_css_unit(max_height),
        "--bslib-card-body-max-height-full-screen": validate_css_unit(
            max_height_full_screen
        ),
        "margin-top": "auto",
        "margin-bottom": "auto",
        # .card-body already adds `flex: 1 1 auto` so make sure to override it
        "flex": "1 1 auto" if fill else "0 0 auto",
        "gap": validate_css_unit(gap),
        "height": validate_css_unit(height),
    }
    tag = tags.div(
        *args,
        {
            "class": "card-body",
            "style": css(**div_style_args),
        },
        class_=class_,
        **kwargs,
    )

    return CardItem(
        bind_fill_role(tag, item=fill, container=fillable),
    )


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class WrapperCallable(Protocol):
    def __call__(self, *args: TagChild) -> CardItem:
        ...


def _as_card_items(
    *children: TagChild | CardItem | None,  # `TagAttrs` are not allowed here
    wrapper: WrapperCallable | None,
) -> list[CardItem]:
    # We don't want `None`s creating empty card bodies
    children_vals = [child for child in children if child is not None]

    attrs, children_vals = consolidate_attrs(*children_vals)
    if len(attrs) > 0:
        raise ValueError("`TagAttrs` are not allowed in `_as_card_items(*children=)`.")

    if not callable(wrapper):
        ret: list[CardItem] = []
        for child in children_vals:
            if isinstance(child, CardItem):
                ret.append(child)
            else:
                ret.append(CardItem(child))
        return ret

    # Any children that are `is.card_item` should be included verbatim. Any
    # children that are not, should be wrapped in card_body(). Consecutive children
    # that are not card_item, should be wrapped in a single card_body().
    state = "asis"  # "wrap" | "asis"
    new_children: list[CardItem] = []
    children_to_wrap: list[TagChild] = []

    def wrap_children():
        nonlocal children_to_wrap
        wrapped_children = wrapper(*children_to_wrap)
        new_children.append(wrapped_children)
        children_to_wrap = []

    for child in children_vals:
        if isinstance(child, CardItem):
            if state == "wrap":
                wrap_children()
            state = "asis"
            new_children.append(child)
        else:
            # Not a card, collect it for wrapping
            state = "wrap"
            children_to_wrap.append(child)
    if state == "wrap":
        wrap_children()

    return new_children


def _wrap_children_in_card(
    *children: TagChild | CardItem | None,  # `TagAttrs` are not allowed here
    wrapper: WrapperCallable | None,
) -> list[TagChild]:
    card_items = _as_card_items(*children, wrapper=wrapper)
    tag_children = [card_item.resolve() for card_item in card_items]
    return tag_children


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class TagCallable(Protocol):  # Should this be exported from htmltools?
    def __call__(
        self,
        *args: TagChild | TagAttrs,
        _add_ws: bool = True,
        **kwargs: TagAttrValue,
    ) -> Tagifiable:
        ...


# TODO-maindocs; @add_example()
def card_title(
    *args: TagChild | TagAttrs,
    container: TagCallable = tags.h5,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    """
    Card title container

    A general container for the "title" of a [card()]. This component is designed
    to be provided as a direct child to :func:`~shiny.experimental.ui.card()`.

    Parameters
    ----------
    *args
        Contents to the card's title. Or tag attributes that are supplied to the
        resolved `Tag` object.
    container
        Method for the returned Tag object. Defaults to :func:`~shiny.ui.h5`.
    **kwargs
        Additional HTML attributes for the returned Tag.

    Returns
    -------
    :
        A Tag object.

    See Also
    --------
    * :func:`~shiny.experimental.ui.card()` for creating a card component.
    * :func:`~shiny.experimental.ui.card_header()` for creating a header within the card.
    * :func:`~shiny.experimental.ui.card_body()` for putting content inside the card.
    * :func:`~shiny.experimental.ui.card_footer()` for creating a footer within the card.
    * :func:`~shiny.experimental.ui.card_image()` for adding an image to the card.
    """
    return container(*args, **kwargs)


# TODO-maindocs; @add_example()
def card_header(
    *args: TagChild | TagAttrs,
    container: TagCallable = tags.div,
    **kwargs: TagAttrValue,
) -> CardItem:
    """
    Card header container

    A general container for the "header" of a [card()]. This component is designed
    to be provided as a direct child to :func:`~shiny.experimental.ui.card()`.

    The header has a different background color and border than the rest of the card.

    Parameters
    ----------
    *args
        Contents to the header container. Or tag attributes that are supplied to the
        resolved `Tag` object.
    container
        Method for the returned Tag object. Defaults to :func:`~shiny.ui.div`.
    **kwargs
        Additional HTML attributes for the returned Tag.

    Returns
    -------
    :
        A `~shiny.experimental.ui.CardItem` object.

    See Also
    --------
    * :func:`~shiny.experimental.ui.card()` for creating a card component.
    * :func:`~shiny.experimental.ui.card_title()` for creating a title within the card body.
    * :func:`~shiny.experimental.ui.card_body()` for putting content inside the card.
    * :func:`~shiny.experimental.ui.card_footer()` for creating a footer within the card.
    * :func:`~shiny.experimental.ui.card_image()` for adding an image to the card.
    """
    return CardItem(
        container({"class": "card-header"}, *args, **kwargs),
    )


# TODO-maindocs; @add_example()
def card_footer(
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> CardItem:
    """
    Card footer container

    A general container for the "footer" of a [card()]. This component is designed
    to be provided as a direct child to :func:`~shiny.experimental.ui.card()`.

    The footer has a different background color and border than the rest of the card.

    Parameters
    ----------
    *args
        Contents to the footer container. Or tag attributes that are supplied to the
        resolved `Tag` object.
    **kwargs
        Additional HTML attributes for the returned Tag.

    Returns
    -------
    :
        A `~shiny.experimental.ui.CardItem` object.

    See Also
    --------
    * :func:`~shiny.experimental.ui.card()` for creating a card component.
    * :func:`~shiny.experimental.ui.card_title()` for creating a title within the card body.
    * :func:`~shiny.experimental.ui.card_body()` for putting content inside the card.
    * :func:`~shiny.experimental.ui.card_footer()` for creating a footer within the card.
    * :func:`~shiny.experimental.ui.card_image()` for adding an image to the card.
    """
    return CardItem(
        tags.div({"class": "card-footer"}, *args, **kwargs),
    )


class ImgContainer(Protocol):
    def __call__(self, *args: Tag) -> Tagifiable:
        ...


# TODO-maindocs; @add_example()
def card_image(
    file: str | Path | PurePath | io.BytesIO | None,
    *args: TagAttrs,
    href: Optional[str] = None,
    border_radius: Literal["top", "bottom", "all", "none"] = "top",
    mime_type: Optional[str] = None,
    class_: Optional[str] = None,
    height: Optional[CssUnit] = None,
    fill: bool = True,
    width: Optional[CssUnit] = None,
    # Required so that multiple `card_images()` are not put in the same `card()`
    container: ImgContainer = card_body,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    """
    Card image container

    A general container for an image within a [card()]. This component is designed to be
    provided as a direct child to :func:`~shiny.experimental.ui.card()`.

    Parameters
    ----------
    file
        A file path pointing an image. The image will be base64 encoded and provided to
        the `src` attribute of the `<img>`. Alternatively, you may set this value to
        `None` and provide the `src` yourself via `*args:TagAttrs` or
        `**kwargs:TagAttrValue` (e.g. `{"src": "HOSTED_PATH_TO_IMAGE"}` or
        `src="HOSTED_PATH_TO_IMAGE"`).
    *args
        Dictionary of tag attributes that are supplied to the resolved `Tag` object.
    href
        An optional URL to link to.
    border_radius
        Where to apply `border-radius` on the image.
    mime_type
        The mime type of the `file`.
    class_
        Additional CSS classes for the resolved Tag.
    height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen` (in this case, consider setting a `height` in
        :func:`~shiny.experimental.ui.card_body()`).
    fill
        Whether to allow this element to grow/shrink to fit its `card()` container.
    width
        Any valid CSS unit (e.g., `width="100%"`).
    container
        Method to wrap the returned Tag object. Defaults to :func:`~shiny.ui.card_body`.
        If :func:`~shiny.ui.card_body` is used, each image will be in separate cards. If
        the `container` method does not return a `~shiny.experiemental.ui.CardItem`, it
        allows for consecutive non-`CardItem` objects to be bundled into a single
        `card_body()` within :func:`~shiny.experiemental.ui.card()`.
    **kwargs
        Additional HTML attributes for the resolved Tag.
    """
    src = None
    if file is not None:
        if isinstance(file, io.BytesIO):
            b64_str = base64.b64encode(file.read()).decode("utf-8")
            if mime_type is None:
                raise ValueError(
                    "`mime_type` must be provided when passing an in-memory buffer"
                )
            src = f"data:{mime_type};base64,{b64_str}"

        elif isinstance(file, (str, Path, PurePath)):
            with open(file, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode("utf-8")
                if mime_type is None:
                    mime_type = mimetypes.guess_type(file)[0]
                src = f"data:{mime_type};base64,{b64_str}"

    card_class_map = {
        "all": "card-img",
        "top": "card-img-top",
        "bottom": "card-img-bottom",
    }

    image = tags.img(
        {
            "src": src,
            "class": "img-fluid",
            "style": css(
                height=validate_css_unit(height),
                width=validate_css_unit(width),
            ),
        },
        {"class": card_class_map.get(border_radius, None)},
        *args,
        class_=class_,
        **kwargs,
    )

    image = bind_fill_role(image, item=fill)

    if href is not None:
        image = as_fill_carrier(tags.a(image, href=href))

    if container:
        return container(image)
    else:
        return CardItem(image)
