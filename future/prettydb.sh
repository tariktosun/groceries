# prettdb.sh
# Uses a sed call to put newlines into an otherwise ugly database dump file.
# Usage:
#   bash prettydb.sh [ugly] > [pretty]

sed 's/{\"pk/\n\n{\"pk/g' $1
