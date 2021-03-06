# Imports
import sys
import argparse
import json
import os

# Contants
PLUGINS_MODULES = r'c:\users\ittai\pycharmprojects\analyzer\venv\src\plugins_modules'
CONFIG_FILE = r"c:\users\ittai\pycharmprojects\analyzer\venv\src\config"

class analyzer:

    def __init__(self, destination, path, plugins):

        self.destination = destination
        self.path = path
        self.plugins = plugins
        self.start_analyzer()

    def start_analyzer(self):
        """
        Starting the analyzer and run all of the plugins
        :return: None
        """

        # Change directory to the plugins directory
        sys.path.insert(1, PLUGINS_MODULES)

        # Import all the plugins
        for module_name in filter(lambda x: x.endswith("py"), os.listdir(PLUGINS_MODULES)):
            exec ("import {0}".format(module_name[:-3]))

        # Run all the plugins the user activate
        for plugin in self.plugins:

             if plugin:
                 exec("{0}.{0}()".format(plugin))

def get_plugins_by_config(config_file, parser):
    """
    Get all the plugins from the config file and add arguemnts for every plugin
    :param config_file: The config file
    :param parser: The argument parser object
    :return: None
    """

    # Read the content of the config file
    with open(CONFIG_FILE, "r") as config_file:
        config_raw = config_file.read()

    # Convert the content of the config file to json
    config_json = json.loads(config_raw)

    # Get all the plugins from the config file
    plugins = config_json["plugins"].keys()

    # For every plugin, add argument to the parser
    for plugin in plugins:

        plugin_json = config_json["plugins"][plugin]
        parser.add_argument(plugin_json["short_flag"], plugin_json["long_flag"], action="store_true")


def main():

    # Create argument parser and add destination and path arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--destination")
    parser.add_argument("-p", "--path")

    # Create arguments from the config file
    get_plugins_by_config(CONFIG_FILE,parser)

    # Get the arguments from the config file
    args = vars(parser.parse_args())
    destination = args.pop("destination")
    path = args.pop("path")
    plugins = args

    # Run analyzer
    analyzer(destination,path,plugins)

if __name__ == "__main__":
    main()


