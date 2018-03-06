# Description
This is a simple webapp for extracting rich content from a journal stored as a text file in the following format:
```
2000-1-1
This is an example of the formatting of the journal.

2000-1-2
Each entry is simply a date header on its own line in the form of YYYY-MM-DD. Anything after a date header but before the next one (or the end of the file) is the body of the entry.
```

# Getting Started

This project requires Python 3. 

## Dependencies
You will `pipenv` to get started.

Install `pipenv` with `pip3 install --user pipenv`.

From the repo root execute `pipenv install`.

To start the application with one command execute use `pipenv run python -m webapp` or `pipenv run flask run`.

This project is distributed as a python package and can be executed directly with `python -m webapp`.