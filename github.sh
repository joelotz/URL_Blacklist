#!/bin/bash

cd ~/Python/github/Projects/URL_Blacklist
echo -e "Enter commit message: \c "
read  word

git add .
git commit -m \"$word\"
git push

