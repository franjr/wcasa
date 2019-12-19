# Working Copy Authorship Static Analysis
Some big projects require several involved committers. Sometimes is not clear the ownership of the committed source code, and using the TortoiseSVN statistic tools points to the whole repository, without a clear differentiation of the files. For instance, the tests are sometimes included as part of the authoring, as well as other documents and files which are part of the repository.

This static analysis tool enables the static analysis of C and H code, checked out as a local working copy.

The tool explores recursively all directories, looking up source and header C files, blaming (using svn blame) each individual file, and extracting the authorship, discarding comments and empty lines.

## Usage
It is required to have an pyhton interpreter installed in your machine.

The usage is as follows:
```python
python wcasa.py your_working_copy_base_folder [from_revision]
```

The result provides complete statistics over explored working copy folder, including the number of analysed files, the total number of lines of files, the number of lines containing source code, the number of empty lines, and the number of comments.

In addition, the list of commiter usernames are displayed, including the number of lines and the percentage of authorship.

The main limitation is that the tool only refers to the latest commited version, so, it does not explore the real contribution itself.
