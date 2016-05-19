import click
from gbdxcli import pass_context


@click.group()
def s3():
    """GBDX S3 Interface"""
    pass

# Required for dynamic import
cli = s3


@s3.command()
@pass_context
def info(ctx):
    """Display the s3 information for this GBDX User"""
    ctx.show(ctx.gbdx.s3.info)
