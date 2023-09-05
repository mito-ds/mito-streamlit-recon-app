#!/bin/bash -eu

echo "Resetting app"

# Clear the outputs director
rm -rf outputs/
mkdir outputs

# Remove the metadata file
rm -rf recon_metadata.csv

# Remove all of the pages that are not called 🆕Recon.py
mkdir tmp
mv Pages/🆕Recon.py /tmp

# Remove all files in the directory
rm -rf Pages/*

# Move the preserved file back to the original directory
mv /tmp/🆕Recon.py Pages/
rm -rf tmp

echo "Finished resetting app"




