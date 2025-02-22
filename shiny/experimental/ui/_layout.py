from __future__ import annotations

from typing import Optional

from htmltools import TagAttrs, TagAttrValue, TagChild, css, div

from ..._typing_extensions import Literal
from ._css_unit import CssUnit, validate_css_unit
from ._fill import as_fillable_container, bind_fill_role
from ._utils import consolidate_attrs, is_01_scalar


def layout_column_wrap(
    width: Optional[CssUnit],
    *args: TagChild | TagAttrs,
    fixed_width: bool = False,
    heights_equal: Literal["all", "row"] = "all",
    fill: bool = True,
    fillable: bool = True,
    height: Optional[CssUnit] = None,
    height_mobile: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    # For
    # more explanation and illustrative examples, see
    # [here](https://rstudio.github.io/bslib/articles/cards.html#multiple-cards)
    """
    A grid-like, column-first layout

    Wraps a 1d sequence of UI elements into a 2d grid. The number of columns (and rows)
    in the grid dependent on the column `width` as well as the size of the display.

    Parameters
    ----------
    width
        The desired width of each card, which can be any of the following:
        * A (unit-less) number between 0 and 1.
            * This should be specified as `1/num`, where `num` represents the number
            of desired columns.
        * A CSS length unit
            * Either the minimum (when `fixed_width=False`) or fixed width
            (`fixed_width=True`).
        * `None`
            * Allows power users to set the `grid-template-columns` CSS property
            manually, either via a `style` attribute or a CSS stylesheet.
    *args
        Unnamed arguments should be UI elements (e.g., [card()]). Named arguments become
        attributes on the containing [htmltools::tag] element.
    fixed_width
        Whether or not to interpret the `width` as a minimum (`fixed_width=False`) or
        fixed (`fixed_width=True`) width when it is a CSS length unit.
    heights_equal
        If `"all"` (the default), every card in every row of the grid will have the same
        height. If `"row"`, then every card in _each_ row of the grid will have the same
        height, but heights may vary between rows.
    fill
        Whether or not to allow the layout to grow/shrink to fit a fillable container
        with an opinionated height (e.g., `page_fillable()`).
    fillable
        Whether or not each element is wrapped in a fillable container.
    height
        Any valid CSS unit to use for the height.
    height_mobile
        Any valid CSS unit to use for the height when on mobile devices (or narrow
        windows).
    gap
        Any valid CSS unit to use for the gap between columns.
    class_
        A CSS class to apply to the containing element.
    **kwargs
        Additional attributes to apply to the containing element.


    """
    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)

    colspec: str | None = None
    if width is not None:
        if is_01_scalar(width) and width > 0.0:
            num_cols = 1.0 / width
            if not num_cols.is_integer():
                raise ValueError(
                    "Could not interpret `layout_column_wrap(width=)` argument"
                )
            colspec = " ".join(["1fr" for _ in range(int(num_cols))])
        else:
            width_css_unit = validate_css_unit(width)
            if fixed_width:
                colspec = f"repeat(auto-fit, minmax({width_css_unit}, 1fr))"
            else:
                colspec = f"repeat(auto-fit, minmax(0, {width_css_unit}))"

    # Use a new dict so that we don't mutate the original `children` dict
    upgraded_children: list[TagChild] = []
    for child_value in children:
        upgraded_children.append(
            as_fillable_container(
                div(bind_fill_role(div(child_value), container=fillable, item=True)),
            )
        )
    tag_style_css = {
        "grid-template-columns": colspec,
        "grid-auto-rows": "1fr" if (heights_equal == "all") else None,
        # Always provide the `height:auto` default so that the CSS variable
        # doesn't get inherited in a scenario like
        # layout_column_wrap(height=200, layout, layout_column_wrap(...))
        "--bslib-column-wrap-height": validate_css_unit(
            "auto" if height is None else height
        ),
        "--bslib-column-wrap-height-mobile": validate_css_unit(
            "auto" if height_mobile is None else height_mobile
        ),
        "gap": validate_css_unit(gap),
    }

    tag = div(
        {
            "class": "bslib-column-wrap",
            "style": css(**tag_style_css),
        },
        attrs,
        *upgraded_children,
    )

    return bind_fill_role(tag, item=fill)
