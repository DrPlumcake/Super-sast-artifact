
![Security check - super-sast-action](https://github.com/DrPlumcake/super-sast-action/workflows/super-sast-action/badge.svg)

# super-sast-action

This [GitHub Action]("https://github.com/features/actions") runs Super SAST,  a docker image that runs several SAST checks on your code, and annotates the interested lines with the reported issues.

Super SAST repository can be checked [here](https://github.com/par-tec/super-sast/) for a better understanding of how it works. This action implements all the tools also used by Super SAST. The version used of Super SAST container is fixed, now is:

```Dockerfile
FROM ghcr.io/par-tec/super-sast:20231115-108-746a559 as super-sast
```

Currently, four tools supports annotations:
- Bandit
- Safety
- Checkov
- Semgrep

## Warning

If you want to enable annotations in your Pull request, you must add a token in the inputs of the action, like this:

```yml
- name: super-sast-action
      uses: DrPlumcake/super-sast-action@v1.0
      with:
        # [...]
        repo_token: ${{ secrets.GITHUB_TOKEN }}
```

Otherwise, the action will fail and the requests will return an error for failing the authentication. 
### Screenshots

The action is run in the workflow:

![](assets/action_1.jpg)

The interested LoC are shown in the PR

![](assets/action_2.jpg)







## Usage

To add this Github action to your repository you can either run it copying it under your repo or via the Github Action Marketplace, eg:

```yml
name: Security check - super-sast-action

on: push

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ ubuntu-latest ]
    name: Ubuntu - ${{ matrix.os }} 

    steps:
    - uses: actions/checkout@v2

    - name: Security check - super-sast-action
      uses: DrPlumcake/super-sast-action@v1.0
      with:
        project_path: .
        ignore_failure: true
        repo_token: ${{ secrets.GITHUB_TOKEN }}

    # This is optional
    - name: Security check artifacts
      uses: actions/upload-artifact@v1
      with:
        name: Security report - super sast
        path: |
          super-sast.log
          log_dir/
```


## Getting Started

You can include the action in your workflow to trigger on any event that
 [GitHub actions supports](https://help.github.com/en/articles/events-that-trigger-workflows). 
 If the remote branch that you wish to deploy to doesn't already exist the action will create it for you. 
 Your workflow will also need to include the `actions/checkout` step before this workflow runs 
 in order for the deployment to work.


If you'd like to make it so the workflow only triggers on push events
 to specific branches then you can modify the `on` section.

```yml
on:
  push:
    branches:
      - master
```
## Configuration

The `with` portion of the workflow **must** be configured before the action will work.
 You can add these in the `with` section found in the examples above. 
 Any `secrets` must be referenced using the bracket syntax and stored 
 in the GitHub repositories `Settings/Secrets` menu. 
 You can learn more about setting environment variables 
 with GitHub actions [here](https://help.github.com/en/articles/workflow-syntax-for-github-actions#jobsjob_idstepsenv).
## Contributing

Contributions are always welcome!

This project uses [pre-commit](https://pre-commit.com/) to manage git hooks. To install the hooks, run:

```bash
pre-commit install
```

Pre-commit will generate a CycloneDX SBOM using trivy.

To test the image, run:

```bash
docker-compose up --build test
```

To test the remote image (latest), run:

```bash
docker-compose up --build test-latest
```


### License

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

