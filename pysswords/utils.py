import os
import shutil


def which(program):
    """Mimics behavior of UNIX which command. """
    # Add .exe program extension for windows support
    try:
        return shutil.which(program)
    except AttributeError:
        if os.name == "nt" and not program.endswith(".exe"):
            program += ".exe"

        for envdir in os.environ["PATH"].split(os.pathsep):
            program_path = os.path.join(envdir, program)
            if os.path.isfile(program_path) and os.access(
                    program_path, os.X_OK):
                return program_path
