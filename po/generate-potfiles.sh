#!/bin/sh

cd "$(dirname "$(realpath "$0")")/.."

echo "# generated on $(date -u)" > ./po/POTFILES

echo "" >> ./po/POTFILES
echo "./data/org.cvfosammmm.Lemma.appdata.xml" >> ./po/POTFILES

echo "" >> ./po/POTFILES
find ./lemma -name '*.py' | sort >> ./po/POTFILES
