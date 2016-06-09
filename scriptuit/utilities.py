#!/usr/bin/env python
"""
A collection of utilities for the generating pipelines. Mostly for getting
subject numbers/names, checking paths, gathering information, etc.
"""

import os, sys

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
        raise TypeError('Input must be a list!')

    # sort the input list
    item_list.sort()

    # print the options, and their numbers
    numbered_list = []
    for i, item in enumerate(item_list):
        numbered_list.append('{}: {}'.format(str(i+1), item))
    print_list(numbered_list)

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
    if n == 2:
        l.sort()
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
    f.write(command)
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

def get_opts(header, args):
    """
    Returns the options for the module as a list.
    The options are found in square brackets in-line with each option, e.g.,
    n_repeats    Number of times to repeat operation on input [int]
    """
    options = {}

    for arg in args:
        optline = filter(lambda x: x.split(' ')[0] == '{}:'.format(arg)
                               and x.count('[') == 1
                               and x.count(']') == 1, header)
        if len(optline) == 1:
            opt = optline[0].split('[')[1].split(']')[0]
            options[arg] = opt

    return options

def get_line(header, pattern):
    """
    Finds a line of the header starting with the defined pattern. Returns
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

def parse(module):
    """
    Parses a scriptuit header, finding prerequisites, output prefixes, and
    module arguments. Asks the user a series of questions to
    """
    header  = get_header(module)
    prereq  = get_line(header, 'prereq:')
    output  = get_line(header, 'output:')
    args    = get_line(header, os.path.basename(module))
    options = get_opts(header, args)

    for h in header:
        print(h)

    if len(output) > 1:
        raise SyntaxError('ERROR: More than one output defined for {}'.format(module))

    # loop through options dictionary and build up command line
    command = os.path.basename(module)

    for opt in options.keys():
        print('\n{}: {}'.format(opt, ' '.join(get_line(header, '{}:'.format(opt)))))
        if options[opt].startswith('list'):
            response = sit.utilities.selector_list(options[opt].split(':')[1].strip().split(' '))
        elif options[opt].startswith('float'):
            response = sit.utilities.selector_float()
        elif options[opt].startswith('int'):
            response = sit.utilities.selector_int()
        else:
            raise SyntaxError('ERROR: malformed option found in module header.')

        # check if we got a reasonable response, construct command if we did
        if response:
            command = '{} {}'.format(command, response)
        else:
            command = None

    return prereq, output, command

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

