def _reset_sys_path():
    # Clear generic sys.path[0]
    import os
    import sys

    resources = os.environ["RESOURCEPATH"]
    while sys.path[0] == resources:
        del sys.path[0]


_reset_sys_path()


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
                print("Image: failed to import")

        if Image.OPEN or Image.SAVE:
            Image._initialized = 2
            return 1

    Image.init = init


_recipes_pil_prescript(['PcdImagePlugin', 'FitsStubImagePlugin', 'PpmImagePlugin', 'ImtImagePlugin', 'PixarImagePlugin', 'SgiImagePlugin', 'GbrImagePlugin', 'TgaImagePlugin', 'PsdImagePlugin', 'WebPImagePlugin', 'FliImagePlugin', 'PdfImagePlugin', 'ImImagePlugin', 'GifImagePlugin', 'JpegImagePlugin', 'MicImagePlugin', 'WmfImagePlugin', 'DcxImagePlugin', 'CurImagePlugin', 'FpxImagePlugin', 'BufrStubImagePlugin', 'Hdf5StubImagePlugin', 'Jpeg2KImagePlugin', 'EpsImagePlugin', 'BmpImagePlugin', 'PcxImagePlugin', 'IcnsImagePlugin', 'DdsImagePlugin', 'PalmImagePlugin', 'TiffImagePlugin', 'IptcImagePlugin', 'SpiderImagePlugin', 'IcoImagePlugin', 'PngImagePlugin', 'XbmImagePlugin', 'McIdasImagePlugin', 'MpoImagePlugin', 'BlpImagePlugin', 'FtexImagePlugin', 'MpegImagePlugin', 'XVThumbImagePlugin', 'GribStubImagePlugin', 'MspImagePlugin', 'XpmImagePlugin', 'SunImagePlugin'])


def _setup_ctypes():
    import os
    from ctypes.macholib import dyld

    frameworks = os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks")
    dyld.DEFAULT_FRAMEWORK_FALLBACK.insert(0, frameworks)
    dyld.DEFAULT_LIBRARY_FALLBACK.insert(0, frameworks)


_setup_ctypes()


DEFAULT_SCRIPT='__main__.py'
SCRIPT_MAP={}
_run()
