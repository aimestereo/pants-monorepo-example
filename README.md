# Example monorepo setup using pants

## Structure

General approach:

* apps - where executable apps live
* libs - place for shared libraries

Dependencies in example repo:

* `apps/example-app-1` depends on `libs/example-lib-core`

* `apps/example-app-2` depends on `libs/example-lib-extended`
  `libs/example-lib-extended` depends on `libs/example-lib-core`

Apps dependencies works:

```sh
> python apps/example-app-1/main.py
Example app 1, model: Model(pk=1)

> python apps/example-app-2/main.py
Example app 2, model: ExtendedModel(pk=1, name='test')
```
