#!/usr/bin/env python
"""
A collection of utilities for the generating pipelines. Mostly for getting
subject numbers/names, checking paths, gathering information, etc.
"""

import os, sys
import re

def selector_float():
    """
    Prompts the user to input a floating-point number.
    """
    option = raw_input('#: ') # have the user enter a number

    # ensure response is non-negative
    if option == 'stop':
        return 'stop'
    if option == '':
        option = -1

    # check input
    try:
        if float(option) >= float(0):
            response = float(option)
            return response
        else:
            print('ERROR: input must be positive.')
            return None
    except:
        print('ERROR: input must be a float.')
        return None

def selector_int():
    """
    Prompts the user to input a integer number.
    """
    option = raw_input('#: ') # have the user enter a number

    if option == 'stop':
        return 'stop'
    if option == '':
        option = -1

    # check input
    try:
        if int(option) >= 0:
            response = int(option)
            return response
        else:
            print('ERROR: input must be positive.')
            return None
    except:
        print('ERROR: input must be an integer.')
        return None

def selector_list(item_list):
    """
    Prompts the user to select from an item in the supplied list.
    """
    if type(item_list) != list:
        raise TypeError('ERROR: input to selector_list must be a list!')

    # sort the input list
    item_list.sort()

    # print the options, and their numbers
    numbered_list = []
    for i, item in enumerate(item_list):
        numbered_list.append('{}: {}'.format(str(i+1), item))
    print_list_cols(numbered_list)

    # retrieve the option number
    option = raw_input('option #: ')

    # check input
    if option == 'stop':
        return 'stop'
    if option == '':
        option = 0

    try:
        response = item_list[int(option)-1]
    except:
        print('ERROR: option # invalid.')
        return None

    if int(option) == 0:
        print('ERROR: option # invalid.')
        return None

    if response == '?':
        response = raw_input('custom input: ')
        response.strip(' ')

    return response

def print_list(lst):
    """
    Prints all the items in a list.
    """
    for item in lst:
        print('    {}'.format(item))

def print_list_cols(l):
    """
    Prints a list in two columns, real pretty like.
    """
    while len(l) % 3 != 0:
        l.append(" ")

    split = len(l)/3
    l1 = l[0:split]
    l2 = l[split:split*2]
    l3 = l[split*2:]

    l = [l1, l2, l3]

    for x in zip(*l):
        print "{0:<25s} {1:<25s} {2}".format(*x)

def has_permissions(directory):
    if os.access(directory, 7) == True:
        flag = True
    else:
        print('ERROR: No write access to directory {}'.format(directory))
        flag = False
    return flag

def check_os():
    """
    Ensures the user isn't Bill Gates.
    """
    import platform

    operating_system = platform.system()
    if operating_system == 'Windows':
        sys.exit('ERROR: Windows detected. scriptuit requires Unix-like OS.')

def touch(f):
    """
    Touches the file f. Used to create placeholders for actual stage outputs
    in scriptuit folders (to save on disk space).
    """
    with open(f, 'a'):
        os.utime(f, None)

def purge(files, replace=False):
    """
    Takes a list of filenames and attempts to remove them.
    """
    if len(files) > 0:
        for f in files:
            os.remove(f)
            if replace:
                touch(f)

def find_files(directory, include, exclude=None, level=1):
    """
    Finds all files in the given directory including some pattern, and
    excluding any directories matching some pattern if defined.
    """
    fnames = []
    assert os.path.isdir(directory)
    num_sep = directory.count(os.path.sep) # n dirs already in the supplied path
    for pth, dirs, files in os.walk(directory, topdown=True):

        # remove directories lower that n levels
        num_sep_this = pth.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

        # exclude files (protected)
        if exclude:
            dirs[:] = [d for d in dirs if exclude not in d]

        for f in files:
            if include in f:
                fnames.append(os.path.join(pth, f))
    yield fnames
    return

def writer(f, p_list, command):
    """
    Writes lines to the master script.
    """
    f.write(command+'\n')
    p_list.append(command)

    return p_list

def get_date_user():
    """
    Returns a human timestamp, the UID, and a machine timestamp.
    """
    import time
    import getpass

    datetime = time.strftime("%Y/%m/%d -- %H:%M:%S")
    user = getpass.getuser()
    f_id = time.strftime("%y%m%d")

    return datetime, user, f_id

def mangle_string(string):
    """
    Turns an arbitrary string into a decent foldername/filename
    (no underscores allowed)!
    """
    string = string.replace(' ', '-')
    string = string.strip(",./;'[]\|_=+<>?:{}!@#$%^&*()`~")
    string = string.strip('"')

    return string

def get_subj(directory):
    """
    Gets all folder names (i.e., subjects) in a directory (of subjects).
    Removes hidden folders.
    """
    subjects = []
    for subj in os.walk(directory).next()[1]:
        if os.path.isdir(os.path.join(directory, subj)) == True:
            subjects.append(subj)
    subjects.sort()
    subjects = filter(lambda x: x.startswith('.') == False, subjects)

    return subjects

def get_header(filename):
    """
    Returns each line of the module header as a list.
    """
    header = []
    f = open(filename, 'rb')

    for i, l in enumerate(f.readlines()):

        # check for shebang
        if i == 0:
            if not l.startswith('#!/bin/bash'):
                raise SyntaxError('ERROR: module {} does not contain BASH shebang'.format(filename))

        # parse header until the comments dissapear
        else:
            if l[0] == '#':
                l = l.lstrip('#').rstrip('\n').strip()
                header.append(l)
            else:
                break

    return header

def get_body(filename):
    """
    Returns each line of the module body as a list.
    """
    body = []
    header = True

    f = open(filename, 'rb')

    for i, l in enumerate(f.readlines()):

        # check for shebang
        if i == 0:
            if not l.startswith('#!/bin/bash'):
                raise SyntaxError('ERROR: module {} does not contain BASH shebang'.format(filename))

        # skip header
        if header:
            if l[0] == '#':
                continue
            else:
                body.append(l)
                header = False
                continue

        body.append(l)
        #body.append(l.rstrip('\n').strip())

    return body

def get_opts(header, args):
    """
    Returns the options for the module as a list of lists.
    The options are found in square brackets in-line with each option, e.g.,
    n_repeats    Number of times to repeat operation on input [int]
    """
    options = []
    if not args:
        return None

    for arg in args:
        optline = filter(lambda x: x.split(' ')[0] == '{}:'.format(arg)
                               and x.count('[') == 1
                               and x.count(']') == 1, header)
        if len(optline) == 1:
            opt = optline[0].split('[')[1].split(']')[0]
            options.append([arg, opt])

    return options

def get_line(header, pattern):
    """
    Finds a entry in a list starting with the defined pattern. Returns
    everything else on that line as a list. Removes all empty values, if none
    are found, returns None.
    """
    for h in header:
        h = h.strip('# \n').lstrip(' ')
        if h.startswith(pattern):

            # remove empty fields, and the prereq tag
            h = filter(lambda x: '' != x, h.split(' '))
            h.remove(pattern)
            if len(h) == 0:
                return None
            else:
                return(h)

def get_rendered_module(moduleBody, line):
    """
    Takes the moduleBody list (obtained with get_body()) and the matching line
    from the master script to fill in all command-line arguments. This 'hard-
    codes' the rendered script.
    """
    for i, arg in enumerate(line.split(' ')):
        if i == 0:
            continue

        # find reference to BASH-format command line argument e.g., ${1} or $1
        regex1 = re.compile('\$\{' + str(i) + '\}')
        regex2 = re.compile('\$' + str(i))
        for j, moduleLine in enumerate(moduleBody):
            if regex1.search(moduleLine):
                moduleBody[j] = moduleLine.replace('${' + str(i) + '}', arg)
                break
            elif regex2.search(moduleLine):
                moduleBody[j] = moduleLine.replace('$' + str(i), arg)
                break
            else:
                pass

    return moduleBody

def check_match(a, b):
    """
    Checks if prerequisite a matches any item in b, ignoring cases.
    """
    for item in b:
        r = re.compile('^{}'.format(a.lower().replace('*','+')))
        if r.match(item.lower()):
            return

    # if we get this far, nothing was matched
    raise ValueError('ERROR: prerequisite {} not met'.format(a))

def check_prerequisites(prerequisites, usedModules):
    """
    For each prerequisite in the list 'prerequisites', ensures there is a
    matching entry in the list 'usedModules'. Any prerequisite can contain a
    wildcard e.g., init_*, which will accept any used module starting with
    'init_'. This isn't case sensitive.

    If this function fails for any prerequisite, it raises an exception.
    """
    for prereq in prerequisites:
        try:
            check_match(prereq, usedModules)
        except:
            print('Prerequisites:')
            print_list(prerequisites)
            raise

def parse(module, usedModules=[], outputFiles=[], verbose=False):
    """
    Parses a scriptuit header. First this checks prerequisites modules have been
    run. It then records the output prefix, and asks the user a series of
    questions to fill in the module arguments.

    Returns the module name and the full string that should be passed to the
    master scriptuit file.
    """
    moduleName = os.path.basename(module)
    header  = get_header(module)
    prereq  = get_line(header, 'prereq:')
    output  = get_line(header, 'output:')
    args    = get_line(header, moduleName)
    options = get_opts(header, args)

    if verbose:
        for h in header:
            print(h)

    if args:
        n_inputs = len(filter(lambda x: 'input' == x.lower(), args))
    else:
        n_inputs = 0

    if output:
        assert len(output) == 1, 'ERROR: More than one output defined for {}'.format(moduleName)
    inputFile = None # useless default value ... to remove?

    if prereq:
        try:
            check_prerequisites(prereq, usedModules)
        except:
            raise

    # get the input name from the last item in the used list
    if n_inputs > 0:
        assert n_inputs == 1, 'ERROR: More than one input defined for {}'.format(moduleName)
        assert len(outputFiles) > 0, 'ERROR: module {} has input defined but no outputs have been generated yet'.format(moduleName)
        inputFile = outputFiles[-1] # always use the most recent file as input

    if verbose:
        print('# of inputs: {}'.format(n_inputs))
        print('output name: {}'.format(output))
        print('module name: {}'.format(moduleName))
        print('input name:  {}'.format(inputFile))
        print('output list: {}'.format(outputFiles))
        print('module list: {}'.format(usedModules))

    # initialize the command with the module name and input if required
    if n_inputs == 0:
        command = moduleName
    else:
        command = '{} {}'.format(moduleName, inputFile)

    if options:
        # loop through options list and build up command line
        for opt in options:

            print('\n{}: {}'.format(opt[0], ' '.join(get_line(header, '{}:'.format(opt[0])))))

            if opt[1].startswith('list'):
                response = selector_list(opt[1].split(':')[1].strip().split(' '))
            elif opt[1].startswith('float'):
                response = selector_float()
            elif opt[1].startswith('int'):
                response = selector_int()
            else:
                raise SyntaxError('ERROR: malformed option found in module {} header.'.format(moduleName))

            if response:
                command = '{} {}'.format(command, response)
            else:
                raise ValueError

    # append output file name to list
    if output:
        outputFiles.append(output[0]) # output is returned as a list

    return outputFiles, command

def print_dirs(in_dir):
    """
    Prints the directories found within the input directory.
    """
    dir_list = [d for d in os.listdir(in_dir) if
                           os.path.isdir(os.path.join(in_dir, d)) == True]
    dir_list.sort()
    for d in dir_list:
        print('    + ' + d)
    if len(dir_list) == 0:
        print('None found.')

