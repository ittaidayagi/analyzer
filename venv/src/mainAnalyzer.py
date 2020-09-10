import sys
import argparse
import json
import os

PLUGINS_MODULES = r'c:\users\ittai\pycharmprojects\analyzer\venv\src\plugins_modules'
CONFIG_FILE = r"c:\users\ittai\pycharmprojects\analyzer\venv\src\config"

class analyzer:

    def __init__(self, destination, path, plugins):

        self.destination = destination
        self.path = path
        self.plugins = plugins
        self.start_analyzer()

    def start_analyzer(self):

        sys.path.insert(1, PLUGINS_MODULES)
        for module_name in filter(lambda x: x.endswith("py"), os.listdir(PLUGINS_MODULES)):
            exec ("import {0}".format(module_name[:-3]))

        for plugin in self.plugins:

             if plugin:
                 exec("{0}.{0}()".format(plugin))

def get_plugins_by_config(config_file, parser):

    with open(CONFIG_FILE, "r") as config_file:
        config_raw = config_file.read()

    config_json = json.loads(config_raw)

    plugins = config_json["plugins"].keys()

    for plugin in plugins:

        plugin_json = config_json["plugins"][plugin]
        parser.add_argument(plugin_json["short_flag"], plugin_json["long_flag"], action="store_true")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--destination")
    parser.add_argument("-p", "--path")

    get_plugins_by_config(CONFIG_FILE,parser)

    args = vars(parser.parse_args())
    destination = args.pop("destination")
    path = args.pop("path")
    plugins = args

    analyzer(destination,path,plugins)

if __name__ == "__main__":
    main()


