#!/bin/sh

# Build the mac distributable
# Executes all other scripts in order


DIR=$(readlink -f $(dirname $0))

echo "Reading config..."
source "$DIR/config.sh" || exit 1
echo "Building $APP_NAME..."

if [ "$CODESIGN_IDENTITY" = "UNKNOWN" ]; then
  echo "No Codesigning identity provided! Abort."
  exit 1
fi

echo "Calling pyinstaller..."
pyinstaller --noconfirm "$DIR/bundle.spec" || exit 1

echo "Signing bundle..."
source "$DIR/sign.sh" || exit 1

echo "Creating image..."
source "$DIR/package.sh" || exit 1

echo "Notarizing..."
source "$DIR/notarize.sh" || exit 1

echo "Success!"
