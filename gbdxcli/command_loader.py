import click
import os
import sys


CMD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__)))

class CommandLoader(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(CMD_FOLDER):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('gbdxcli.cmd_' + name,
                             None, None, ['cli'])
        except ImportError as e:
            print e
            return
        return mod.cli
