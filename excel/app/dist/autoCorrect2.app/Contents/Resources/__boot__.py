def _reset_sys_path():
    # Clear generic sys.path[0]
    import sys
    import os

    resources = os.environ["RESOURCEPATH"]
    while sys.path[0] == resources:
        del sys.path[0]


_reset_sys_path()


def _emulate_shell_environ():
    import os
    import sys
    import time

    if sys.version_info[0] > 2:
        env = os.environb
    else:
        env = os.environ

    split_char = b"="

    # Start 'login -qf $LOGIN' in a pseudo-tty. The pseudo-tty
    # is required to get the right behavior from the shell, without
    # a tty the shell won't properly initialize the environment.
    #
    # NOTE: The code is very carefull w.r.t. getting the login
    # name, the application shouldn't crash when the shell information
    # cannot be retrieved
    try:
        login = os.getlogin()
        if login == "root":
            # For some reason os.getlogin() returns
            # "root" for user sessions on Catalina.
            try:
                login = os.environ["LOGNAME"]
            except KeyError:
                login = None
    except AttributeError:
        try:
            login = os.environ["LOGNAME"]
        except KeyError:
            login = None

    if login is None:
        return

    master, slave = os.openpty()
    pid = os.fork()

    if pid == 0:
        # Child
        os.close(master)
        os.setsid()
        os.dup2(slave, 0)
        os.dup2(slave, 1)
        os.dup2(slave, 2)
        os.execv("/usr/bin/login", ["login", "-qf", login])
        os._exit(42)

    else:
        # Parent
        os.close(slave)
        # Echo markers around the actual output of env, that makes it
        # easier to find the real data between other data printed
        # by the shell.
        os.write(master, b'echo "---------";env;echo "-----------"\r\n')
        os.write(master, b"exit\r\n")
        time.sleep(1)

        data = []
        b = os.read(master, 2048)
        while b:
            data.append(b)
            b = os.read(master, 2048)
        data = b"".join(data)
        os.waitpid(pid, 0)

    in_data = False
    for ln in data.splitlines():
        if not in_data:
            if ln.strip().startswith(b"--------"):
                in_data = True
            continue

        if ln.startswith(b"--------"):
            break

        try:
            key, value = ln.rstrip().split(split_char, 1)
        except Exception:
            pass

        else:
            env[key] = value


_emulate_shell_environ()


def _chdir_resource():
    import os

    os.chdir(os.environ["RESOURCEPATH"])


_chdir_resource()


def _disable_linecache():
    import linecache

    def fake_getline(*args, **kwargs):
        return ""

    linecache.orig_getline = linecache.getline
    linecache.getline = fake_getline


_disable_linecache()


import re
import sys

cookie_re = re.compile(br"coding[:=]\s*([-\w.]+)")
if sys.version_info[0] == 2:
    default_encoding = "ascii"
else:
    default_encoding = "utf-8"


def guess_encoding(fp):
    for _i in range(2):
        ln = fp.readline()

        m = cookie_re.search(ln)
        if m is not None:
            return m.group(1).decode("ascii")

    return default_encoding


def _run():
    global __file__
    import os
    import site  # noqa: F401

    sys.frozen = "macosx_app"
    base = os.environ["RESOURCEPATH"]

    argv0 = os.path.basename(os.environ["ARGVZERO"])
    script = SCRIPT_MAP.get(argv0, DEFAULT_SCRIPT)  # noqa: F821

    path = os.path.join(base, script)
    sys.argv[0] = __file__ = path
    if sys.version_info[0] == 2:
        with open(path, "rU") as fp:
            source = fp.read() + "\n"
    else:
        with open(path, "rb") as fp:
            encoding = guess_encoding(fp)

        with open(path, "r", encoding=encoding) as fp:
            source = fp.read() + "\n"

        BOM = b"\xef\xbb\xbf".decode("utf-8")
        if source.startswith(BOM):
            source = source[1:]

    exec(compile(source, path, "exec"), globals(), globals())


def _recipes_pil_prescript(plugins):
    try:
        import Image

        have_PIL = False
    except ImportError:
        from PIL import Image

        have_PIL = True

    import sys

    def init():
        if Image._initialized >= 2:
            return

        if have_PIL:
            try:
                import PIL.JpegPresets

                sys.modules["JpegPresets"] = PIL.JpegPresets
            except ImportError:
                pass

        for plugin in plugins:
            try:
                if have_PIL:
                    try:
                        # First try absolute import through PIL (for
                        # Pillow support) only then try relative imports
                        m = __import__("PIL." + plugin, globals(), locals(), [])
                        m = getattr(m, plugin)
                        sys.modules[plugin] = m
                        continue
                    except ImportError:
                        pass

                __import__(plugin, globals(), locals(), [])
            except ImportError:
                if Image.DEBUG:
                    print("Image: failed to import")

        if Image.OPEN or Image.SAVE:
            Image._initialized = 2
            return 1

    Image.init = init


_recipes_pil_prescript(['Hdf5StubImagePlugin', 'FitsStubImagePlugin', 'SunImagePlugin', 'IptcImagePlugin', 'GbrImagePlugin', 'PngImagePlugin', 'Jpeg2KImagePlugin', 'MicImagePlugin', 'FpxImagePlugin', 'PcxImagePlugin', 'ImImagePlugin', 'SpiderImagePlugin', 'PsdImagePlugin', 'BufrStubImagePlugin', 'SgiImagePlugin', 'BlpImagePlugin', 'XpmImagePlugin', 'DdsImagePlugin', 'MpoImagePlugin', 'BmpImagePlugin', 'TgaImagePlugin', 'PalmImagePlugin', 'XVThumbImagePlugin', 'GribStubImagePlugin', 'PdfImagePlugin', 'ImtImagePlugin', 'FtexImagePlugin', 'GifImagePlugin', 'CurImagePlugin', 'McIdasImagePlugin', 'MpegImagePlugin', 'IcoImagePlugin', 'TiffImagePlugin', 'PpmImagePlugin', 'MspImagePlugin', 'EpsImagePlugin', 'JpegImagePlugin', 'PixarImagePlugin', 'PcdImagePlugin', 'WmfImagePlugin', 'FliImagePlugin', 'DcxImagePlugin', 'IcnsImagePlugin', 'WebPImagePlugin', 'XbmImagePlugin'])


def _setup_ctypes():
    from ctypes.macholib import dyld
    import os

    frameworks = os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks")
    dyld.DEFAULT_FRAMEWORK_FALLBACK.insert(0, frameworks)
    dyld.DEFAULT_LIBRARY_FALLBACK.insert(0, frameworks)


_setup_ctypes()


DEFAULT_SCRIPT='autoCorrect2.py'
SCRIPT_MAP={}
_run()
