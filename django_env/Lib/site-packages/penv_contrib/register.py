# -*- coding: utf-8 -*-
"""A set of buildin penv plugins.
"""
import os
from os.path import (
    join as pjoin,
    isdir,
    exists,
)
import penv


class VirtualenvPlugin(penv.Plugin):
    def on_activate(self, root_new, root_old):
        venv = self.config.TRIGGER
        default_file = root_new(venv, 'default')
        default_env = root_new(venv, 'env')

        if exists(default_file):
            virtualenv_name = open(default_file, "r").read().replace("\n", "")
            virtualenv_path = root_new(venv, virtualenv_name)

            if isdir(virtualenv_path):
                return [self.bash.source(pjoin(virtualenv_path, 'bin', 'activate'))]
            else:
                return ["workon %s" % virtualenv_name]
        else:
            if isdir(default_env):
                return [self.bash.source(pjoin(default_env, 'bin', 'activate'))]

    def on_deactivate(self, root_new, root_old):
        if os.environ.get("VIRTUAL_ENV"):
            return ["deactivate 2>/dev/null"]


class CustomScriptsPlugin(penv.Plugin):
    def on_activate(self, root_new, root_old):
        script = root_new(self.config.TRIGGER, 'on_activate')
        if exists(script):
            return [self.bash.source(script)]

    def on_deactivate(self, root_new, root_old):
        script = root_old(self.config.TRIGGER, 'on_deactivate')
        if exists(script):
            return [self.bash.source(script)]


class PENV_EnvVariablesPlugin(penv.Plugin):
    def on_activate(self, root_new, root_old):
        venv_dir = root_new(self.config.TRIGGER)
        if exists(venv_dir):
            return [
                self.bash.export("VENV_ROOT", venv_dir),
                self.bash.export("VENV_ROOT_PARENT", root_new()),
            ]

    def on_deactivate(self, root_new, root_old):
        venv_dir = root_old(self.config.TRIGGER)
        if exists(venv_dir):
            return [
                self.bash.unset("VENV_ROOT"),
                self.bash.unset("VENV_ROOT_PARENT"),
            ]


penv.registry.add(
    PENV_EnvVariablesPlugin,
    VirtualenvPlugin,
    CustomScriptsPlugin,
)
