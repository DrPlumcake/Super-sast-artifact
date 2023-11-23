#!/bin/sh -l

echo "🔥🔥🔥🔥🔥Running security check🔥🔥🔥🔥🔥🔥"

#env variables
export GITHUB_TOKEN=$INPUT_REPO_TOKEN
export M2_HOME=$INPUT_M2_HOME
export HOME=$INPUT_HOME
export BANDIT_CONFIG_FILE=$INPUT_BANDIT_CONFIG_FILE
export RUN_LOCAL=$INPUT_LOCAL

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
