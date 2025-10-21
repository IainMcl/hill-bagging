# Hill bagging

This project aims to get and store hill data from Walkhighlands.
The aim of this is to use the data to find efficient routes and orders for
bagging hills.

The long term aim is to be able to find the time and distance from a home
location to each walk with the option of maximising bagging efficiency by
getting the most peaks in walks per distance traveled.

## Coding standards

* All methods should have a docstring explaining their purpose. This should not be a repeat of the method name.
* Logging should not use f strings but should use the `extra` parameter to pass in variables.
* All code should be type hinted.
* I don't like when tests have `# Arrange`, `# Act`, `# Assert` comments. Please avoid using these.

## Project structure

Tests should be stored in an app level test structure like this:

```
src/
    module1/
        __init__.py
        module1_code.py
        tests/
            __init__.py
            test_module1_code.py
    module2/
        __init__.py
        module2_code.py
        tests/
            __init__.py
            test_module2_code.py
```
This keeps the tests close to the code they are testing and makes it easier
to find the tests for a specific module.

## Running tests

To run the tests, use the following command from the root of the project:

```bash
uv run pytest src/
```

## Writing tests

Tests using database access should use a test database. The test database
should be created and destroyed for each test run to ensure a clean state.

Database models should use facotories to create test data. This ensures thau

## Dependencies

Dependencies are managed using `uv`.
