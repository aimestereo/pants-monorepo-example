# Example monorepo setup using pants

## Structure

General approach:

* apps - where executable apps live
* libs - place for shared libraries

Dependencies in example repo:

* `apps/example-app-1` depends on `libs/example-lib-core`

* `apps/example-app-2` depends on `libs/example-lib-extended`
  `libs/example-lib-extended` depends on `libs/example-lib-core`

* except for `apps/example-app-1` all other `pyproject.toml` have explicit dependency `pydantic`. Basically all packages depends on `pydantic`, here I test if having explicit or implicit dependency affects the result.

Apps dependencies works:

```sh
> python apps/example-app-1/main.py
Example app 1, model: Model(pk=1)

> python apps/example-app-2/main.py
Example app 2, model: ExtendedModel(pk=1, name='test')
```

## Pants

I run all reported commands after killing pants daemon, as docs saying it should kill the cache, and without it warnings are hidden on the second run:
```sh
> ps aux | grep pants | grep -v grep | awk '{print $2}' | xargs kill -9
```

```sh
> pants dependencies --transitive apps/example-app-1
01:11:58.78 [INFO] Initializing scheduler...
01:12:02.63 [INFO] Scheduler initialized.
01:12:04.11 [WARN] The target libs/example-lib-core/example_lib_core/schema.py imports `pydantic.BaseModel`, but Pants cannot safely infer a dependency because more than one target owns this module, so it is ambiguous which to use: ['apps/example-app-2:poetry#pydantic', 'libs/example-lib-core:poetry#pydantic', 'libs/example-lib-extended:poetry#pydantic'].

Please explicitly include the dependency you want in the `dependencies` field of libs/example-lib-core/example_lib_core/schema.py, or ignore the ones you do not want by prefixing with `!` or `!!` so that one or no targets are left.

Alternatively, you can remove the ambiguity by deleting/changing some of the targets so that only 1 target owns this module. Refer to https://www.pantsbuild.org/v2.16/docs/troubleshooting#import-errors-and-missing-dependencies.
01:12:04.11 [WARN] Pants cannot infer owners for the following imports in the target libs/example-lib-core/example_lib_core/schema.py:

  * pydantic.BaseModel (line: 1)

If you do not expect an import to be inferrable, add `# pants: no-infer-dep` to the import line. Otherwise, see https://www.pantsbuild.org/v2.16/docs/troubleshooting#import-errors-and-missing-dependencies for common problems.
```

How should I solve this:

> Please explicitly include the dependency you want in the `dependencies` field of libs/example-lib-core/example_lib_core/schema.py, or ignore the ones you do not want by prefixing with `!` or `!!` so that one or no targets are left.

my attemps:

1. add explicit library dependencies to `libs/example-lib-core/BUILD`:

```python
__defaults__(all=dict(dependencies=["libs/example-lib-core:poetry"],))
```

Partial success:

```sh
> pants dependencies --transitive apps/example-app-1
00:57:22.42 [INFO] Initializing scheduler...
00:57:26.65 [INFO] Scheduler initialized.
00:57:28.15 [WARN] Pants cannot infer owners for the following imports in the target libs/example-lib-core/example_lib_core/schema.py:

  * pydantic.BaseModel (line: 1)

If you do not expect an import to be inferrable, add `# pants: no-infer-dep` to the import line. Otherwise, see https://www.pantsbuild.org/v2.16/docs/troubleshooting#import-errors-and-missing-dependencies for common problems.
3rdparty/python/default.lock:_python-default_lockfile
apps/example-app-1/pyproject.toml:poetry
libs/example-lib-core/example_lib_core/schema.py
libs/example-lib-core/pyproject.toml:poetry
libs/example-lib-core:poetry#pydantic
```

2. adding build target to `apps/example-app-1/BUILD` doesn't help:

```python
pex_binary(
    name="app-1",
    entry_point="main.py",

    interpreter_constraints=["==3.10.*"],

    execution_mode='venv',
    dependencies=[
        # these doesn't help final result
        # ":poetry",
        # "libs/example-lib-core:poetry",
    ],
)
```

3. (just example, not a part of the repo) on other project, I also tried to turn libraries to actual libraries, didn't helped with warnings:

`libs/example-lib-core/BUILD`
```
__defaults__(all=dict(dependencies=["libs/example-lib-core:poetry"],))

poetry_requirements(
    name="poetry",
)

python_distribution(
    name="lib",
    dependencies=[
        # Dependencies on code to be packaged into the distribution.
        ":poetry",
        "./example_lib_core",
    ],
    provides=python_artifact(
        name="example-lib-core",
        version="0.1.0",
    ),
    # Example of setuptools config, other build backends may have other config.
    wheel_config_settings={"--global-option": ["--python-tag", "py310"]},
    # Don't use setuptools with a generated setup.py.
    # You can also turn this off globally in pants.toml:
    #
    # [setup-py-generation]
    # generate_setup_default = false
    generate_setup = False,
)
```
