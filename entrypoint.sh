#!/bin/sh -l

echo "🔥🔥🔥🔥🔥Running security check🔥🔥🔥🔥🔥🔥"

#env variables
GITHUB_TOKEN=$INPUT_REPO_TOKEN
M2_HOME=$INPUT_M2_HOME
HOME=$INPUT_HOME
BANDIT_CONFIG_FILE=$INPUT_BANDIT_CONFIG_FILE

python /main.py

if [ "$?" -eq 0 ]; then
    echo "🔥🔥🔥🔥Security check passed🔥🔥🔥🔥"
    exit 0
fi

echo "🔥🔥🔥🔥Security check failed🔥🔥🔥🔥"
if $INPUT_IGNORE_FAILURE; then
    exit 0
fi

exit 1
