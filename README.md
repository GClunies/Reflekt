<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
Reflekt enables anyone using dbt to **automagically build a dbt package that models and documents all the events in a tracking plan** pulled from an Analytics Governance tool, ready for use in a dbt project. Each Reflekt dbt package includes:
- A dbt [source](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in the warehouse where the raw event data is loaded.
- A dbt [model](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for each event in the tracking plan. Ready for consumption or use in downstream models.
- A dbt [doc](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) entry for every event modeled in the package, pulling information *directly from the tracking plan*. The data team and the business always know what your models and columns mean.

https://user-images.githubusercontent.com/28986302/171330405-57400ead-574d-4b71-a31b-57935e0ba9e8.mp4

## Getting Started
Install Reflekt with `pip`.
```bash
pip install reflekt
```

  - [How it works](#how-it-works)
  - [Reflekt Documentation](docs/DOCUMENTATION.md/#reflekt-docs)
    - [Create a Reflekt project](docs/DOCUMENTATION.md/#create-a-reflekt-project)
    - [Project configuration](docs/DOCUMENTATION.md/#project-configuration)
    - [Tracking plans as `code`](docs/DOCUMENTATION.md/#tracking-plans-as-code)
    - [Commands](docs/DOCUMENTATION.md/#commands)
  - [Usage](#usage)
    - [Using Reflekt + Avo](#using-reflekt--avo)
    - [Using Reflekt + Segment Protocols](#using-reflekt--segment-protocols)
  - [Reporting bugs](#reporting-bugs)
  - [Contributing code](#contributing-code)


## How it works
Reflekt connects with your Analytics Governance tool (e.g. [Segment Protocols](https://segment.com/docs/protocols/), [Avo](https://www.avo.app/)), your Data Warehouse (e.g. [Snowflake](https://www.snowflake.com/)), and [dbt](https://www.getdbt.com/).

![reflekt-architecture](/docs/reflekt-arch-flow.jpg)

Using these connections, Reflekt defines tracking plans as `code`, making them extensible artifacts that can power downstream uses - like templating dbt packages. This code can also be used to **manage tracking plans using software engineering principles** (version control, branches, pull requests, reviews, and CI/CD).

## Usage

https://user-images.githubusercontent.com/28986302/171340104-f4a6f989-4c6b-4ca9-985c-c482c7e234e0.mp4


### Using Reflekt + Avo
[Avo](https://www.avo.app/) uses branches, environments, and naming conventions to manage tracking plans, bringing a workflow similar to software engineering into their web based UI.

**For Avo users, its recommended to continuing manage tracking plans in Avo, then connecting Reflekt to Avo** (see the docs on [Connecting Reflekt + Avo](DOCUMENTATION.md/#connecting-reflekt--avo)). With this setup, you can:
- Pull the tracking plan from Avo as it changes (can specify Avo branch) into Reflekt.
  ```bash
  reflekt pull --name my-plan --avo-branch staging
  ```
  This creates a copy of the plan as code in the Reflekt project, to be used by Reflekt's dbt templater.

- Template a dbt package modeling and documenting all the events in the tracking plan. You can tell Reflekt to template based on data in specified schema (configure available schemas for plans in `reflekt_project.yml`).
  ```bash
  reflekt dbt --name my-plan --schema my_app_staging
  ```

- Open a GitHub pull request with new/updated Reflekt dbt package. Get reviews from team members. Merge to main branch when approved.

- Reference Reflekt dbt packages in your dbt project.
  ```yaml
  # packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  - git: "https://github.com/my-github-user/reflekt-project-repo"
    subdirectory: "dbt_packages/reflekt_my_app_staging"
    revision: v0.1.0__reflekt_my_app_staging  # Git tag or full commit
  ```

In the example above, Reflekt know's about Avo's staging branch and the staging schema in the data warehouse, allowing you to assess how tracking plan changes will affect downstream dbt models ***before pushing tracking changes to production.***

### Using Reflekt + Segment Protocols
[Segment Protocols](https://segment.com/docs/protocols/) lets you manage tracking plans within your Segment account. While Segment does not use branches and environments,  Reflekt leverages Segment's APIs to bring software workflows to managing Segment Protocols tracking plans (version control, development branches, pull requests, reviews, and CI/CD).

**For Segment Protocols users, its recommended to manage your tracking plans as `code`** in a GitHub repository containing your Reflekt project. With this setup, you can:
- Make changes to a tracking plan (e.g. add new event) by changing the tracking plan code.
  ```yaml
  # Adding a new event is easy!
  version: 1
  name: Example Event
  description: This is an example event.
  metadata:
    code_owner: me
  properties:
    name: example_property
    description: This is an example property.
    type: string
    required: true
  ```
- Template a dbt package modeling and documenting all the events in the tracking plan.
  ```bash
  reflekt dbt --name my-plan --schema my_app
  ```
- Open pull requests in GitHub. Request reviews from team members, debate, and collaborate.
- Trigger a GitHub Action CI suite on pull request open, checking that tracking plan changes meet follow your naming conventions and metadata expectations.
  <details><summary><strong>test-plans-github-action.yml</strong> (CLICK TO EXPAND EXAMPLE)</summary><p>

  ```yaml
  # test-plans-github-action.yml

  name: Test Tracking Plans
  on: pull_request

  jobs:
    test:
      name: Test Tracking Plans
      strategy:
        fail-fast: false
        matrix:
          os: ['ubuntu-latest']
          python-version: ['3.9']
      runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v2
      - name: Install Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python: ${{ matrix.python-version }}
      - name: Install Reflekt
        run: |
          pip install reflekt
      - name: Run reflekt test
        run: |
          reflekt test --name my-plan
  ```
  </p></details>

- On merge to main branch in GitHub, automatically your updated tracking plan code to Segment Protocols using a GitHub Action. Reflekt handles the conversion for you.
  <details><summary><strong>sync-plans-github-action.yml</strong> (CLICK TO EXPAND EXAMPLE)</summary><p>

  ```yaml
  # sync-plans-github-action.yml

  name: Sync Tracking Plans
  on: pull_request

  jobs:
    test:
      name: Sync Tracking Plans
      strategy:
        fail-fast: false
        matrix:
          os: ['ubuntu-latest']
          python-version: ['3.9']
      runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v2
      - name: Install Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python: ${{ matrix.python-version }}
      - name: Install Reflekt
        run: |
          pip install reflekt
      - name: Run reflekt test
        run: |
          reflekt push --name my-plan
  ```
  </p></details>

- Reference Reflekt dbt packages in your dbt project.
  ```yaml
  # packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  - git: "https://github.com/my-github-user/reflekt-project-repo"
    subdirectory: "dbt_packages/reflekt_my_app"
    revision: v0.1.0__reflekt_my_app  # Git tag or full commit
  ```

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls) for contributions you would like to propose.

#### Development environment
reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment.

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
