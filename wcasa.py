

##
#The current program explores for a working copy, checked out from a subversion
#repository, the authorship of the C/C++ commits using the blame command.
#
# Only the *.c and *.h files are explored.
#
#The difference w.r.t. svn blame is that the authorship blame only applies
#to the working copy instead to the subversion repository.
#
#If a revision is provided in addition as an input parameter, the authorship
#is only calculated from a given revision.
#

'''
@author: franjr
@version: 1.0
'''

import os
import sys
import subprocess
import collections
import re
import fnmatch

## Determines the name of the program.
TOOLNAME = "Working Copy Authorship Static Analysis (wcasa)"

## The current version.
VERSION = "V1.0"

## The reference revision from which the code is explored.
ref_revision = 0

## Determines the filter for the files to be processed.
filter_list = ['*.c', '*.h']

## Determines the exclusion list of the folder which should not be processed.
exclusion_list = ['.svn', 'test']

class WCASA(object):
    ## The dictionary containing the pairs author,lines-of-code.
    _authorship_dict = {}

    ## The total number of explored files.
    _number_files = 0

    ## The total number of lines of explored code.
    _total_lines = 0
    
    ## The total number of source code lines.
    _code_lines = 0
    
    ## The total number of empty lines.
    _empty_lines = 0
    
    ## The total number of commented code.
    _commented_lines = 0

    ## Determines the root folder.
    _root_folder = ""

    def set_entry_path(self, folder):
        self._root_folder = folder

    def explore_working_copy(self, folder, from_rev=0, depth=-1):
        #for root, dirs, files in os.walk(folder):
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            # Obtain the folder name
            folder_name = folder.replace(self._root_folder + '\\', '')
            if os.path.isdir(item_path):
                # Check if this belongs to the exclusion list
                exclusion_match = False
                for exclusion_item in exclusion_list:
                    if not re.match(re.compile(exclusion_item), folder_name) is None:
                        exclusion_match = True
                        break

                if exclusion_match:
                    continue

                if depth == 0:
                    continue
                elif depth < 0:
                    new_depth = depth
                else:
                    new_depth = depth - 1
                self.explore_working_copy(item_path, from_rev, new_depth)
            elif os.path.isfile(item_path):
                filename = str(item)
                filter_match = False
                for filter_item in filter_list:
                    if not re.match(re.compile(fnmatch.translate(filter_item)), filename) is None:
                        filter_match = True
                        break
                
                if not filter_match:
                    continue

                # Add the number of files here.
                self._number_files += 1
                
                # Run the svn blame command for the item.
                blame_output = subprocess.check_output("svn blame " + item_path)

                # Provide user feedback in console
                sys.stdout.write("\rfolder: {}{}file: {}{}".format(folder_name, ' ' * (35 - len(folder_name)), filename, ' ' * (30 - len(filename))))
                sys.stdout.flush()
                
                # Parse the output of the blame command.
                self.parse_output(blame_output, from_rev)

    ## Parses the output of a blame command over a file.
    # @param content The content of the svn blame output on a file.
    # @param from_rev The reference revision.
    def parse_output(self, content, from_rev=0):
        for content_line in content.split("\n"):
            list_content = content_line.split()
            if len(list_content) == 0:
                # Empty content.
                return
            elif len(list_content) == 2:
                # Empty line.
                self._total_lines += 1
                self._empty_lines += 1
            elif len(list_content) > 2:
                revision = list_content[0]
                commiter = list_content[1]
                source_code = list_content[2]
                source_code = source_code.strip()

                # Check if the revision is greater than the reference revision.
                if from_rev > int(revision):
                    continue

                # Process the statistics.
                self._total_lines += 1
                if len(source_code) == 0:
                    self._empty_lines += 1
                elif source_code.startswith("/*"):
                    self._commented_lines += 1
                elif source_code.startswith("//"):
                    self._commented_lines += 1
                else:
                    self._code_lines += 1
                    if commiter in self._authorship_dict:
                        self._authorship_dict[commiter] += 1
                    else:
                        self._authorship_dict[commiter] = 1

    ## Prints the results obtained from running the wcasa explore_working_copy() function.
    def print_results(self):
        print("Authorship Resume:\n==================")
        print("analysed_files=" + str(self._number_files))
        print("lines=" + str(self._total_lines) + "\nlines of code=" + str(self._code_lines))
        print("empty=" + str(self._empty_lines) + "\ncomments=" + str(self._commented_lines))
        print("\nAuthor\t\tLOC\tPercent\t\n========\t=====\t=======")

        # sort the dictionary
        sorted_authorship = collections.OrderedDict(sorted(self._authorship_dict.items(), key=lambda t: t[1], reverse=True))

        for author in sorted_authorship:
            contribution = float(sorted_authorship[author])/float(self._code_lines)
            print("{}{}".format(author,' ' * (8 - len(author))) + "\t" + str("{}{}".format(sorted_authorship[author], ' ' * (8 - len(author)))) + "\t" + "{:.2%}".format(contribution))

## Main program
if __name__ == '__main__':
    print(TOOLNAME + " " + VERSION)
    print("Usage: " + str(sys.argv[0]) + " 'folder_name' [from_revision]")

    # Obtain all the parameters required
    param_number = len(sys.argv)
    if param_number <= 1:
        sys.exit()
    elif param_number > 1:
        explore_dir = sys.argv[1]
        if explore_dir.startswith('.'):
            #resolve path
            cwd = os.getcwd()
            explore_dir = os.path.join(cwd, explore_dir)
        explore_dir = os.path.normpath(explore_dir)
        if param_number > 2:
            ref_revision = int(sys.argv[2])
    
    print("Base folder: " + explore_dir)
    if (param_number > 2):
        print("Base revision: r" + str(ref_revision))

    # Create an instance of the WCASA class.
    wcasa = WCASA()
    
    # Establish the base folder.
    wcasa.set_entry_path(explore_dir)
    
    # Perform the processing of the working copy.
    wcasa.explore_working_copy(explore_dir, from_rev=ref_revision)

    # Clean the output with carriage return.
    sys.stdout.write("\r{}\n".format(' ' * 80))
    sys.stdout.flush()

    # Print the analysis results.
    wcasa.print_results()

