# description of this app in 50 words
# ..



# standard imports
# ..

# internal imports
# ..

# local imports
# ..

# shared imports
# ..

# thirdparty imports
# ..



# pkg const metadata
# ------------------------------------------------------------------------------
NAME = "PLUXSIM"
INFO = 'Simple HTTP server simulating production line data'
AUTH = '-untitled-'
SPAN = '2022-23'
VERS = ''
# ..

# pkg var metadata
# ------------------------------------------------------------------------------
__VER_MAJOR = 0
__VER_MINOR = 3
__VER_PATCH = 0
__VER_BUILD = 48

__IS_PRE_RELEASE = True
__PRE_RELEASE_BUILD = 2

if __IS_PRE_RELEASE:
    VERS = f'{__VER_MAJOR}.{__VER_MINOR}b-{__PRE_RELEASE_BUILD} (Build {__VER_BUILD})'
else:
    VERS = f'{__VER_MAJOR}.{__VER_MINOR}.{__VER_PATCH} (Build {__VER_BUILD})'

# DESCRIPTION = f'{NAME} v{VERS} by {AUTH} {SPAN} is {INFO}'