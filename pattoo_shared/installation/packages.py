"""Functions for installing external packages."""
# Standard imports
import os
import getpass

# Import pattoo related libraries
from pattoo_shared.installation import shared
from pattoo_shared import log


def get_package_version(package_name):
    """Retrieve installed pip package version.

    Args:
        package_name: The name of the package

    Returns:
        package_dict:A dictionary containing the installed packages

    """
    raw_description = shared.run_script('pip3 show {}'.format(package_name))[1]
    pkg_description = raw_description.decode().split('\n')
    version = pkg_description[1].replace(' ', '').split(':')
    return version[1]


def install_missing_pip3(package, verbose=False):
    """Automatically Install missing pip3 packages.

    Args:
        package: The pip3 package to be installed

    Returns:
        None

    """
    # Validate pip directory
    shared.run_script('''\
python3 -m pip install {0} -U --force-reinstall'''.format(package), verbose=verbose)


def install(requirements_dir, installation_directory, verbose=False):
    """Ensure PIP3 packages are installed correctly.

    Args:
        requirements_dir: The directory with the pip_requirements file.
        installation_directory: Directory where packages must be installed.
        verbose: Print status messages if True

    Returns:
        True if pip3 packages are installed successfully

    """
    # Initialize key variables
    lines = []

    # Read pip_requirements file
    filepath = '{}{}pip_requirements.txt'.format(requirements_dir, os.sep)

    # Say what we are doing
    print('Checking pip3 packages')
    if os.path.isfile(filepath) is False:
        shared.log('Cannot find PIP3 requirements file {}'.format(filepath))

    # Opens pip_requirements file for reading
    try:
        _fp = open(filepath, 'r')
    except PermissionError:
        log.log2die_safe(1079, '''\
Insufficient permissions for reading the file: {}. \
Ensure the file has read-write permissions and try again'''.format(filepath))
    else:
        with _fp:
            line = _fp.readline()
            while line:
                # Strip line
                _line = line.strip()
                # Read line
                if True in [_line.startswith('#'), bool(_line) is False]:
                    pass
                else:
                    lines.append(_line)
                line = _fp.readline()
    # Process each line of the file
    for line in lines:
        # Determine the package
        package = line.split('=', 1)[0]
        package = package.split('>', 1)[0]

        # If verbose is true, the package being checked is shown
        if verbose:
            print('Installing package {}'.format(package))
        command = 'python3 -m pip show {}'.format(package)
        (returncode, _, _) = shared.run_script(
            command, verbose=verbose, die=False)

        # Install any missing pip3 package
        if bool(returncode) is True:
            install_missing_pip3(package, verbose=verbose)

    # Check for outdated packages
    if verbose:
        print('Checking for outdated packages')
    for package in lines:
        # Get packages with versions from pip_requirements.txt
        requirement_package = package.split('==', 1)
        if len(requirement_package) == 2:
            installed_version = get_package_version(requirement_package[0])
            # Reinstall package if incorrect version is installed
            if installed_version != requirement_package[1]:
                install_missing_pip3(package, verbose=verbose)

    # Set ownership of any newly installed python packages to pattoo user
    if getpass.getuser() == 'root':
        if os.path.isdir(installation_directory) is True:
            shared.run_script('chown -R pattoo:pattoo {}'.format(
                installation_directory), verbose=verbose)

    print('pip3 packages successfully installed')
