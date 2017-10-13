import os
import sys

class UserConfig(object):
    LOGPACKETS = False
    CABLE_DRIVER = None
    CABLE_NAME = None
    SHOW_CHAIN = True
    SHOW_CABLE = True
    SHOW_CONFIG = True
    SOCKET_ADDRESS = 2222
    root = None

    def loadfile(self, fname):
        if self.root is None:
            self.root = os.path.dirname(sys.argv[0])
        if not os.path.exists(fname):
            fname = os.path.join(self.root, fname)
            if not os.path.exists(fname):
                raise SystemExit("\nCannot find configuration file %s\n" % fname)
        try:
            f = open(fname, 'rb')
            exec f in globals(), vars(self)
            f.close()
        except:
            print "\nError processing %s:\n" % fname
            raise

    def readargs(self, args=None, parseargs=False):
        usesys = args is None
        if usesys:
            args = sys.argv[1:]
        options = []
        for i in range(len(args)-1, -1, -1):
            if '=' in args[i]:
                options.append(args.pop(i).split('=', 1))
        for name, value in reversed(options):
            try:
                value = int(value,0)
            except (TypeError, ValueError):
                pass
            setattr(self, name.upper(), value)
        if usesys:
            sys.argv[1:] = args

        if parseargs and args:
            self.CABLE_DRIVER = args.pop(0)
            if args:
                devname = ' '.join(args)
                try:
                    devname = int(devname, 0)
                except ValueError:
                    pass
                self.CABLE_NAME = devname
        return args, options

    def loaddefault(self, fname, args=None):
        try:
            self.loadfile(fname)
            loaded = True
        except SystemExit, exc:
            loaded = False
        args, options = self.readargs(args)
        if not options and not loaded:
            raise exc
        return args

    def add_defaults(self, other):
        try:
            other = vars(other)
        except TypeError:
            pass
        try:
            other = other.iteritems()
        except AttributeError:
            pass
        for name, value in other:
            if not hasattr(self, name):
                setattr(self, name, value)

    def dump(self):
        result = ['\nConfiguration options:\n',]
        names = set(vars(self)) | set(vars(type(self)))
        names = [x for x in sorted(names) if x[0].isupper()]
        for name in names:
            value = getattr(self, name)
            if isinstance(value, bool):
                value = repr(value)
            elif isinstance(value, float):
                if 0.1 <= value <= 1000:
                    value = '%0.2f' % value
                else:
                    value = '%0.2e' % value
            else:
                try:
                    value = '%-14s # (%d)' % ('0x%x' % value, value)
                except TypeError:
                    value = repr(value)
            result.append('    %-28s = %s' % (name, value))
        result.append('')
        return '\n'.join(result)

    def error(self, errmsg):
        raise SystemExit('\nERROR: %s\n\n%s' % (str(errmsg), self.dump()))

    def deferred_error(self):
        print "\n\nError opening cable driver (details below)\n%s\n" % self.dump()

    def getcable(self):
        for prefix in ('playtag.cables.', ''):
            try:
                modname = prefix + self.CABLE_DRIVER
                return __import__(modname, globals(), locals(), ['Jtagger'])
            except ImportError:
                continue
            break
        else:
            self.error("Could not open cable driver %s" % repr(self.CABLE_DRIVER))
