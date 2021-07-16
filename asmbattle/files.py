import os
import gettext
import logging

PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(PROGRAM_DIR + "/..")
RESOURCE_DIR = ROOT_DIR + "/resources"
if not os.path.exists(RESOURCE_DIR):
    RESOURCE_DIR = os.path.abspath("./resources")
if not os.path.exists(RESOURCE_DIR):
    raise FileNotFoundError(RESOURCE_DIR)

LOCALE_DIR = ROOT_DIR + "/locale"
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = os.path.abspath("./locale")
if not os.path.exists(LOCALE_DIR):
    raise FileNotFoundError(LOCALE_DIR)

ICON_DIR = ROOT_DIR + "/resources/icons"
if not os.path.exists(ICON_DIR):
    ICON_DIR=os.path.abspath("./resources/icons")
if not os.path.exists(ICON_DIR):
    raise FileNotFoundError(ICON_DIR)

def get_resource_filename(name):
    filename = os.path.join(RESOURCE_DIR, name)
    logging.getLogger(__name__).debug("resource: " + filename)
    return filename

def get_icon_filename(name):
    filename =  os.path.join(ICON_DIR, name)
    logging.getLogger(__name__).debug("icon: " + filename)
    return filename

def get_root_filename(name):
    filename =  os.path.join(ROOT_DIR, name)
    if not os.path.exists(filename):
        filename = os.path.joint(".", name)
    logging.getLogger(__name__).debug("root: " + filename)
    return filename

def get_translation(name):
    return gettext.translation(name, LOCALE_DIR, fallback=True)

