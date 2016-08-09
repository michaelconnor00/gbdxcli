import click
from gbdxcli.main import pass_context


@click.group()
def s3creds():
    """GBDX S3 Temporary Credentials Interface"""
    pass

# Required for dynamic import
cli = s3creds


@s3creds.command()
@pass_context
def info(ctx):
    """Display the s3 information for this GBDX User"""
    ctx.show(ctx.gbdx.s3.info)
