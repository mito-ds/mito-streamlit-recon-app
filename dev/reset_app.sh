#!/bin/bash -eu

echo "Resetting app"

# Clear the outputs director
rm -rf outputs/
mkdir outputs

# Clear the recon-scripts directory
rm -rf recon-scripts/
mkdir recon-scripts

# Remove the metadata file
rm -rf recon_metadata.csv

# Remove all of the pages that are not called 🆕Recon.py
mkdir tmp
mv Pages/🆕\ Create\ New\ Recon.py /tmp

# Remove all files in the directory
rm -rf Pages/*

# Move the preserved file back to the original directory
mv /tmp/🆕\ Create\ New\ Recon.py Pages/
rm -rf tmp

echo "Finished resetting app"




