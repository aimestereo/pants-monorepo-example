python_sources()

poetry_requirements(
    name="poetry",
)

pex_binary(
    name="app-2",
    entry_point="main.py",

    interpreter_constraints=["==3.10.*"],

    execution_mode='venv',
    dependencies=[
        # these doesn't help final result
        # ":poetry",
        # "libs/example-lib-core:poetry",
    ],
)

