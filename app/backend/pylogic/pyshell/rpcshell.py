# -*- coding: utf-8
import os
import sys
import atexit
import xmlrpc.client


class Shell(object):
    """ Python консоль с фильтрацией ввода/вывода комманд """

    def __init__(self, server, histfile=os.path.expanduser("~/.pyshell_hist")):
        self.server = server
        self.init_history(histfile)

        try:
            import readline
        except ImportError:
            pass
        else:
            from rlcompleter import Completer
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.server.completer)

    def remote_completer(self, text, state):
        print(text, state)

    def init_history(self, histfile):
        try:
            import readline
        except ImportError:
            pass
        else:
            readline.parse_and_bind("tab: complete")
            if hasattr(readline, "read_history_file"):
                try:
                    readline.read_history_file(histfile)
                except IOError:
                    pass
                atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        try:
            import readline
        except ImportError:
            pass
        else:
            readline.write_history_file(histfile)

    def interact(self, banner='Welcome to remote PyLogic Shell\n!help: list of custom commands'):
        run = True
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        print("%s" % str(banner))
        more = 0
        while run:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = input(prompt)
                    # Can be None if sys.stdin was redefined
                    # encoding = getattr(sys.stdin, "encoding", None)
                    # if encoding and not isinstance(line, unicode):
                    #     line = line.decode(encoding)
                except EOFError:
                    print("\n")
                    break
                else:
                    more = self.push(line)
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt\n")
                more = 0
                run = False

    def push(self, line):
        """ Наши функции """
        if line.startswith('!'):

            cmdAndArgs = line[1:].split()
            cmd = cmdAndArgs[0]
            args = cmdAndArgs[1:]
            func = self.getCommandFunc(cmd)

            if func:
                try:
                    func(*args)
                except Exception as e:
                    sys.stdout.write("= Error: %s\n" % e)
            else:
                sys.stdout.write("No such command\n")

            return False

        res = self.server.interpreter(line)
        print(res[0])
        return res[1]

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    # COMMANDS

    def do_help(self, cmd=''):
        """ Get help on a command. Usage: help command """
        if cmd:
            func = self.getCommandFunc(cmd)
            if func:
                sys.stdout.write(func.__doc__ + '\n')
                return

        publicMethods = filter(
            lambda funcname: funcname.startswith('do_'), dir(self))
        commands = [cmd.replace('do_', '', 1) for cmd in publicMethods]
        sys.stdout.write("Commands: " + " ".join(commands) + "\n")

    def do_dr(self, addr):
        print(self.server.dump_receiver(addr))

    def do_dump_channels(self, type, *name):
        """ Usage: !dump_channels in Paster Doser """
        name = " ".join(name)
        print(name)
        print(type)
        print(self.server.dump_channels(type, name))


def getApplicationShell(server):
    """ Получаем экземпляр консоли текущего приложения """

    print("-" * 55)
    print(
        "INFO: Custom shell is not implemented.\nFor implement Make func shell.getShell(server)\nLoading default pyshell...")
    print("-" * 55)
    return Shell(server)


def main(host='http://localhost:9999'):
    """ Точка входа приложения pyshell """
    s = xmlrpc.client.ServerProxy(host)
    getApplicationShell(s).interact(banner="Welcome to remote PyShell\n!help: list of custom commands")


if __name__ == '__main__':
    url = 'localhost:9999'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    main('http://' + url)
