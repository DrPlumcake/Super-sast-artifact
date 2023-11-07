#!/bin/sh -l

echo "🔥🔥🔥🔥🔥Running security check🔥🔥🔥🔥🔥🔥"

GITHUB_TOKEN=$INPUT_REPO_TOKEN python /main.py 

if [ "$?" -eq 0 ]; then
    echo "🔥🔥🔥🔥Security check passed🔥🔥🔥🔥"
    exit 0
fi

echo "🔥🔥🔥🔥Security check failed🔥🔥🔥🔥"
if $INPUT_IGNORE_FAILURE; then
    exit 0
fi
    
exit 0
