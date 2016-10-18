# -*- coding: utf-8 -*-

import subprocess


def run_command(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    status = p.wait()
    return output.strip().decode('utf-8'), err, status
