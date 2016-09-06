import click
from gbdxcli import pass_context


@click.group()
def ordering():
    """Ordering commands"""
    pass


# Required for dynamic import
cli = ordering


@ordering.command()
@click.option("--catalog_id", "-c",
    multiple=True,
    help="Catalog ID of the strip to order. May pass multiple times")
@pass_context
def order(ctx, catalog_id):
    """Order the catalog ID(s) passed in"""
    if len(catalog_id == 0):
        print "No catalog IDs passed in."
        return
    if len(catalog_id) == 1:
        # pull the one item and just order that
        ctx.show( ctx.gbdx.ordering.order(catalog_id[0]) )
    else:
        # this is a list with multiple entries
        ctx.show( ctx.gbdx.ordering.order(catalog_id) )


@ordering.command()
@click.option("--order_id","-o",
    help="Order ID to status")
@pass_context
def status(ctx, order_id):
    ctx.show( ctx.gbdx.ordering.status(id) )
