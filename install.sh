#!/bin/bash

# Print a message indicating the start of the installation
printf "Installing he-dns\n"

# Ensure the destination directory exists
mkdir -p ~/.local/bin

# Check if he-dns already exists in ~/.local/bin
if [ -f ~/.local/bin/he-dns ]; then
    rm ~/.local/bin/he-dns
fi

# Copy the main executable to the local bin directory and check if the operation was successful
if cp dist/main ~/.local/bin/he-dns; then
    printf "Installation is done!! Enjoy he-dns\n"
else
    printf "Installation failed. Please check if 'dist/main' exists and is executable.\n"
fi
