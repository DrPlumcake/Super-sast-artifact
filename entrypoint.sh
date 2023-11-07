#!/bin/sh -l

echo "🔥🔥🔥🔥🔥Running security check🔥🔥🔥🔥🔥🔥"

dir="log_dir"

if [ -d "$dir" ]; then
    echo "Directory $dir already exists"
else
    if mkdir "$dir"; then
        echo "error during creation of $dir directory"
        exit 1
    fi
fi

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
