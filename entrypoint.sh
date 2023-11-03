#!/bin/sh -l

echo "🔥🔥🔥🔥🔥Running security check🔥🔥🔥🔥🔥🔥"
mkdir -p $GITHUB_WORKSPACE/output
touch $GITHUB_WORKSPACE/output/security_report.txt

# da cambiare le variabili d'ambiente

if [ -f "${INPUT_CONFIG_FILE}" ]; then
    echo "Using config file: ${INPUT_CONFIG_FILE}"
    BANDIT_CONFIG="-c ${INPUT_CONFIG_FILE}"
fi
    echo "Not using config file (test)"

echo "Running bandit with: " ${BANDIT_CONFIG} -r "${INPUT_PROJECT_PATH}" -o "${GITHUB_WORKSPACE}/output/security_report.txt" -f 'txt'
bandit ${BANDIT_CONFIG} -r "${INPUT_PROJECT_PATH}" -o "${GITHUB_WORKSPACE}/output/security_report.txt" -f 'txt'
BANDIT_STATUS="$?"

echo "output of filesystem structure:\n"
mkdir log_dir

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
