# Contributing to django-bulk-save

This project is open to contributions of all kinds and from people of every experience level. Bug reports, ideas, documentation improvements, tests, and code contributions are all welcome.

As an early prototype, the project also welcomes discussion about its design and intended API.

## How to contribute

- Open an issue to report a bug, describing what happened, what you expected, and how to reproduce it.
- Share ideas or discuss larger changes in an issue so we can work through the approach together.
- Submit a pull request with a clear description of the problem and how your changes address it. Include relevant tests or documentation updates when appropriate.

## Running tests

With Python 3.14 or later and a virtual environment activated, install the project with its test dependencies:

```bash
python -m pip install -e ".[test]"
```

The suite uses `pytest` and `pytest-django`. Database tests require PostgreSQL and cover custom pre-save logic, bulk creation, grouped updates through `pgbulk`, and transaction rollback. Follow the [PostgreSQL test instructions](README.md#tests) to configure the connection and run the suite. Context registry tests can run without a database using `python -m pytest tests/test_context.py`. Support for other database engines will be developed upon request; open an issue specifying the engine and use case.

## Be kind and respectful

Please keep every interaction friendly, polite, and respectful, including issues, pull requests, reviews, and other project discussions.

Different opinions and constructive criticism are welcome. Focus feedback on ideas and code, assume good intentions, and be patient with questions and mistakes. Personal attacks, insults, harassment, and discriminatory comments are not acceptable.

The goal is to make contributing a welcoming experience where everyone can learn, share ideas, and improve the project together.
