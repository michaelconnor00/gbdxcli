import click
from gbdxcli import pass_context


@click.group()
def catalog():
    """Catalog commands"""
    pass


# Required for dynamic import
cli = catalog


@catalog.command()
@click.option("--catalog_id", "-c",
    help="Catalog ID of the strip to display")
@pass_context
def strip_footprint(ctx, catalog_id):
    """Show the WKT footprint of the strip named"""
    ctx.show(ctx.gbdx.catalog.get_strip_footprint_wkt(catalog_id))
