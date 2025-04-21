#!/bin/zsh
# File to push the data and plots via git 
WD=$HOME/dev/ghouse 
cd $WD
git add data/ 
git add datavisualisation/figures
git add datacollection/

TODAY=$(date +%Y-%m-%d_%H:%M)
git status
echo pushing data to $TODAY
git commit -m "updaing data $TODAY"
git push origin main 
echo pushed data to $TODAY