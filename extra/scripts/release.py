# Extremely stupid, messy python script that bundles a release shipment for me.
# The code is meant to be obvios and ELI5 level understandable, easily not the
# fastest solution around. 'Might' get improved in the future.
# Sincere apologies if you loose brain cells reading this. Intended though :p


import datetime
import os
import shutil
import subprocess
import sys
import time

global ROOTDIR
ROOTDIR = os.getcwd()

global WORKSPACE
WORKSPACE = f"{ROOTDIR}"

global OUTDIR
OUTDIR = sys.argv[1]

global VERSION
VERSION = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

global PKG_FOLDER
PKG_FOLDER = f'pxsim-{VERSION}'



# ==============================================================================
# ==============================================================================

# docs
# ------------------------------------------------------------------------------
def add_scripts():
    print("Creating runtime scripts")
    launch_scr = '''
    @echo OFF
    cd app/pxsim
    pxsim --config "../../config/pxsim.toml" --stdout"
    pause
    '''
    filepath = f'{OUTDIR}/{PKG_FOLDER}/launch.bat'
    writer = open(filepath, 'w')
    writer.write(launch_scr)
    writer.close()

    return os.path.exists(filepath)


# docs
# ------------------------------------------------------------------------------
def collect_extras():
    return True


# docs
# ------------------------------------------------------------------------------
def generate_docs():
    is_success = os.path.isdir(WORKSPACE)
    coverage_guide = None
    basic_readme   = ''

    def read_from(file_path : str,):
        reader = open(file_path, 'r')
        data = reader.read()
        reader.close()
        return data

    def write_into(file : str, data: str):
        writer = open(file, 'w')
        writer.write(data)
        writer.close()

    if is_success:
        is_success = os.path.isdir(f"{OUTDIR}/{PKG_FOLDER}/docs")

    if is_success:
        coverage_guide = read_from(f"{WORKSPACE}/docs/coverage_test_guide.html")
        is_success     = coverage_guide is not None

    if is_success:
        write_into(
            file = f"{OUTDIR}/{PKG_FOLDER}/docs/coverage_guide.html",
            data = coverage_guide
        )

        write_into(
            file = f'{OUTDIR}/{PKG_FOLDER}/readme.txt',
            data = basic_readme
        )

    return is_success


# docs
# ------------------------------------------------------------------------------
def fill_data():
    is_success = os.path.isdir(WORKSPACE)
    dbcfile = None

    def read_from(file_path : str,):
        reader = open(file_path, 'r')
        data = reader.read()
        reader.close()
        return data

    def write_into(file : str, data: str):
        writer = open(file, 'w')
        writer.write(data)
        writer.close()

    if is_success:
        is_success = os.path.isdir(f'{OUTDIR}/{PKG_FOLDER}/data')

    if is_success:
        dbcfile = read_from(f'{WORKSPACE}/data/can/scm.dbc')
        is_success = dbcfile is not None

    if is_success:
        os.mkdir(f'{OUTDIR}/{PKG_FOLDER}/data/can')
        is_success = os.path.exists(f'{OUTDIR}/{PKG_FOLDER}/data/can')

    if is_success:
        write_into(
            file = f'{OUTDIR}/{PKG_FOLDER}/data/can/scm.dbc',
            data = dbcfile
        )
    
    return is_success


# docs
# ------------------------------------------------------------------------------
def create_config():
    print("Creating configuration")
    is_success = os.path.isdir(WORKSPACE)
    configFile = None
    dbconfigs  = None

    def read_from(file_path : str,):
        reader = open(file_path, 'r')
        data = reader.read()
        reader.close()
        return data

    def write_into(file : str, data: str):
        writer = open(file, 'w')
        writer.write(data)
        writer.close()

    if is_success:
        is_success = os.path.isdir(f'{OUTDIR}/{PKG_FOLDER}/config')

    if is_success:
        configFile = read_from(f'{WORKSPACE}/config/pxsim.toml')
        is_success = configFile is not None

    if is_success:
        configFile = configFile.replace("<<VERSION>>",VERSION)

    if is_success:
        write_into(
            file = f'{OUTDIR}/{PKG_FOLDER}/config/pxsim.toml',
            data = configFile
        )

    return is_success


# docs
# ------------------------------------------------------------------------------
def create_app():
    print("Building executable")
    is_success = os.path.isdir(WORKSPACE)
    
    if is_success:
        is_success = os.path.isdir(f'{OUTDIR}/{PKG_FOLDER}/app')
    
    if is_success:
        is_success = os.path.isfile(f'{WORKSPACE}/source/__main__.py')
        print(f'{WORKSPACE}/source/__main__.py')

    if is_success:
        try:
            subprocess.call(
                args = [
                    'pyinstaller',
                    '--specpath', f'{WORKSPACE}/out/build',
                    '--workpath', f'{WORKSPACE}/out/build',
                    '--distpath', f'{OUTDIR}/{PKG_FOLDER}/app',
                    '--noconfirm',
                    '--onedir',
                    '--console',
                    '--name', 'pxsim',
                    '--clean',
                    f'{WORKSPACE}/source/__main__.py'
                ])
        except Exception as e:
            print(f"ERROR : {e} while generating application")
            is_success = False

    return is_success


# docs
# ------------------------------------------------------------------------------
def create_release_directory():
    print("Creating release directory")
    is_success = False

    if os.path.isdir(OUTDIR):
        release_folder = f'{OUTDIR}/{PKG_FOLDER}'

        if os.path.exists(release_folder):
            shutil.rmtree(release_folder)

        try:
            os.mkdir(release_folder)
            is_success = True
        except Exception as e:
            print(f"ERROR : {e} while creating folder: {release_folder}")

    return is_success


# docs
# ------------------------------------------------------------------------------
def populate_release_directory():
    print("Populating release directory")
    release_folder = f'{OUTDIR}/{PKG_FOLDER}'
    is_success     = os.path.exists(release_folder)
    
    # create folders
    if is_success:
        try:
            os.mkdir(f"{release_folder}/app")
            os.mkdir(f"{release_folder}/config")
            os.mkdir(f"{release_folder}/data")
            os.mkdir(f"{release_folder}/docs")
            os.mkdir(f"{release_folder}/extra")
            os.mkdir(f"{release_folder}/out")

        except Exception as e:
            print(f"ERROR : {e} while populating release folder")
            is_success = False

    # populate each folder with contents
    if is_success:
        is_success = create_app()

    if is_success:
        is_success = create_config()

    # if is_success:
    #     is_success = fill_data()

    # if is_success:
    #     is_success = generate_docs()
    
    #if is_success:
    #    is_success = collect_extras()

    if is_success:
        is_success = add_scripts()

    return is_success


# compress the build into a zip file
# ------------------------------------------------------------------------------
def archive_release_build():
    return True


# docs
# ------------------------------------------------------------------------------
def buildpackage():
    if create_release_directory():
        if populate_release_directory():
            return archive_release_build()


# ------------------------------------------------------------------------------
# Application starts from here
# ------------------------------------------------------------------------------
print(f"\nPackaging pxsim {VERSION} \n")

if buildpackage():
    print(f"\npxsim {VERSION} packaging SUCCESS\n")
else:
    print(f"\npxsim {VERSION} packaging FAILURE\n")