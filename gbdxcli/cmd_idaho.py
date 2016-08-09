import click
from gbdxcli import pass_context


@click.group()
def idaho():
    pass


# Required for dynamic import
cli = idaho


@idaho.command()
@click.option("--catalog_id","-c",
    help="Catalog ID to fetch IDAHO images for")
@pass_context
def get_images_by_catid(ctx, catalog_id):
    """Retrieve all IDAHO Images associated with a catalog ID"""
    ctx.show(ctx.gbdx.idaho.get_images_by_catid(catalog_id))
