import click
from gbdxcli.main import pass_context
from gbdxcli.commands.utils import _s3creds

#
# S3temp command group for temporary credentials
#
@click.group()
def s3temp():
    """S3 Temporary Credentials Interface"""
    pass

# Required for dynamic import
cli = s3temp


@cli.group()
def s3temp():
    """Set temporary S3 credentials for access to GBDX S3 customer-data bucket."""
    pass


@s3temp.command()
@click.option("--awscli/--no-awscli", "-a", help="Set temporary s3 credentials in the awscli config file (~/.aws/credentials) (default: false).", default=False)
@click.option("--awscli_profile", "-o", help="Write the credentials into this profile in the aswcli config file (default: temp).", default="temp")
@click.option("--s3cmd/--no-s3cmd", "-s", help="Set temporary s3 credentials in the s3cmd config file. (default: false)", default=False)
@click.option("--s3cmd_config", help="Name of the s3cmd config file (default: ~/.s3cfg).", default="~/.s3cfg")
@click.option("--environ/--no-environ", "-e", help="Write temporary s3 credentials to stdout. (default: false)", default=False)
@click.option("--environ_export/--no-environ_export", help="Prefix each environment variable with 'export' (default: false).", default=False)
@click.option("--print_token/--no-print_token", "-p", help="Write to the screen the GBDX token information. (default: false)", default=False)
@click.option("--duration", "-d", help="Duration of the S3 credentials in seconds. (default: 36000)", type=click.IntRange(900,36000), default=36000)
@pass_context
def set(ctx, awscli, awscli_profile, s3cmd, s3cmd_config, environ, environ_export, print_token, duration):
    """Writes temporary GBDX S3 credentials to one or more of the following targets:

    awscli -- The Amazon Web Services Command Line Interface (https://aws.amazon.com/cli/) credentials file
    s3cmd -- The Command Line S3 Client (http://s3tools.org/s3cmd) configuration file
    environ -- Bash environment variables (only prints to the screen)

    By design, the GBDX credentials have a duration of at most 36000 seconds

    Warning: No backups of the original files are made!

    """

    if not any((awscli, s3cmd, environ)):
        raise click.ClickException("Must specify at least one of --awscli, --s3cmd or --environ.")

    if print_token:
        _s3creds.print_gbdx_token_info(ctx)

    _s3creds.set_temp_creds(ctx.session, awscli, awscli_profile, s3cmd, s3cmd_config, environ, environ_export, duration)


@s3temp.command()
def clear():
    """Clear temporary data from configuration files."""
    raise click.ClickException("Not Implemented")
