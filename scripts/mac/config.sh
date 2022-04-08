#!/bin/sh

# fill this in or provide from environ
[ ! "$CODESIGN_IDENTITY" ] && CODESIGN_IDENTITY="UNKNOWN"

# program specifics
APP_NAME="MAFFTpy"
APP_IDENTIFIER="org.itaxotools.mafftpy.gui"
APP_SCRIPT="../mafftpy.py"
APP_ENTITLEMENTS="data/entitlements.plist"
APP_ICON="data/mafftpy.icns"


# expand and export
export CODESIGN_IDENTITY=$CODESIGN_IDENTITY
export APP_NAME="$APP_NAME"
export APP_IDENTIFIER="$APP_IDENTIFIER"

DIR=$(readlink -f $(dirname $0))
export APP_SCRIPT="$DIR/$APP_SCRIPT"
export APP_ENTITLEMENTS="$DIR/$APP_ENTITLEMENTS"
export APP_ICON="$DIR/$APP_ICON"

export APP_BUNDLE="$PWD/dist/$APP_NAME.app"
export APP_IMAGE="$PWD/dist/$APP_NAME.dmg"
