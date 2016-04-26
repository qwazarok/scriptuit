![scriptuit](assets/logo.png "scriptuit: a platform for BASH pipeline development")

scriptuit is an environment for developing pipelines out of BASH 'modules'. It is intended to produce portable BASH analysis scripts out of small code chunks that non-programmers can contribute.

Written by Joseph D. Viviano 2014-16.

**Shortcuts:**

+ [Setup](#setup)
+ [Introduction](#introduction)
+ [Modules](#modules)
+ [Data](#data)
+ [Usage](#usage)

Setup
-----
scriptuit depends on python > 2.6. The scripts it generates likely rely on external pacakges.

Quickstart:

+ `git clone` this repository to a directory of your choosing.
+ Add `scriptuit/bin` to your PATH.
+ Add `scriptuit` to your PYTHONPATH.
+ Create a data directory somewhere, and add some data.
+ Set `SCRIPTUIT_DATA` to point to your data folder.
+ Set `SCRIPTUIT_MODULES` to point to a folder containing scriptuit modules.
+ Generate a script using `scriptuit run`.

Optional:

+ [Grid Engine](http://gridscheduler.sourceforge.net/) or [PBS](http://www.adaptivecomputing.com/products/open-source/torque/)

Introduction
------------
scriptuit platform for developing BASH pipelines with a focus on rapid prototyping and ease of reproducibility. It was designed primarily with the needs of experimental researchers in mind. It is able to intelligently chain together BASH modules with a specially formatted header in any way the user desires to create a script for analysing data.

scriptuit facilitates the construction of scripts that can be run on your computer or in a distributed computing environment by only answering a few high-level questions. Scriptuit can be used to render fully self-contained BASH scripts for portability or further tweaking. In this way, scriptuit acts as your lab notebook, and it's outputs can be shared with collaborators or reviewers.

Modules
-------
Modules take the form of BASH scripts with a special header format. They are active so long as they are kept in the `SCRIPTUIT_MODULES` directory.

A scriptuit module has the following in it's header:

    #!/bin/bash
    #
    # module_name input list_variable float_variable int_variable
    #
    # input:          input prefix, to find input files. auto-determined by scriptuit
    # list_variable:  a list of strings for the user to select from [list: apples banannas oranges]
    # float_variable: a number (allows for decimals). [float]
    # int_variable:   a number (no decimals) [int]
    #
    # output: example_output
    # prereq: init_pipeline
    #
    # This is where you can put more details about your module, for people to read.

    input=${1}
    list_variable=${2}
    float_variable=${3}
    int_variable=${4}

scriptuit reads this header in order to ask the user reasonable questions on how to configure this particular module. It finally executes this module with the command line values filled in appropriately. Note that since this module is normal bash, one can execute a module without ever going through the scriptuit interface.

Here's a walk through of the various header components:

**usage** 

    # module_name input list_variable float_variable int_variable

This line contains the name of the module (the file name of the module must match the module name listed here), followed by the names of each command-line argument.

**arguments**

    # input:          input prefix, to find input files. auto-determined by scriptuit
    # list_variable:  a list of strings for the user to select from [list: apples banannas oranges ?]
    # float_variable: a number (allows for decimals). [float]
    # int_variable:   a number (no decimals) [int]

Here, we see the 4 arguments available in scriptuit.

+ `input` is a special argument in scriptuit. It is automatically filled by the `output` prefix of the previous module. Therefore, any module with an input argument should be a mid-stage module. scriptuit modules that are run at the beginning of the pipelines should not have an `input` argument, and should copy files from the `RUNXX` folder. 

+ `list_variable` is a case where the user should select from a set of pre-defined, or custom, strings. The `[list: x y z ?]` syntax at the end of the line is a space-delimited list of the options to be presented to the user. `?` is a special case, that if selected asks the user to enter a custom string.

+ `float_variable` is a case where the user should input a number, including decimals. It is specified by `[float]`.

+ `int_variable` is a case where the user should input a whole number. It is specified by `[int]`.

Each argument in the usage line must have an line under arguments, otherwise the pipeline will fail. 

**flow control**

    # output: example_output
    # prereq: init_pipeline

Here, we see the output prefix (the first part of the filename of the main outputs from this module) and the prerequisite modules, by filename. scriptuit uses the output prefix here to auto-fill the `input` argument for downstream modules. It also ensures that the prerequisite modules have been run.

In this case, init_pipeline is used to copy the files in the RUN folders to the SESS folder with a known file prefix, so that the `example` module know what the input prefix is.

**documentation**

    # This is where you can put more details about your module, for people to read.

This is simply usage instructions for the user. Please write this.

**variable assignment**

    input=${1}
    list_variable=${2}
    float_variable=${3}
    int_variable=${4}

When your scriptuit module is executed, the values selected will be assigned to the BASH variables here. The number of, and names of, these variables should match those in the usage line.

**module anatomy**

A module will typically loop through sessions, and then runs, taking an input file prefix (such as `phys_detrended`), performing a number of operations on that file (producing intermediate files worth keeping, or in other cases, temporary files that will be removed by the module's end), and usually outputting a file (one for each run) with a new prefix (such as `phys_lowpass`). The anatomy of a call to an output file follows the convention

    # general form
    ${input}.${ID}.${run_number}.extension

    # specific form
    ID='example'
    input='func_detrend'
    run_number='01'
    func_detrend.example.01.txt

A well-written module will never try to do anything that has already been done. Therefore, blocks of code should be wrapped in a:

    if [ -f ${input}.${ID}.${run_number}.extension ]; then; 
        commands 
    fi

loop. This is not mandatory, but highly recommended. It allows one to re-run the pipeline with a few tweaks, and the code will only act on files missing from the output structure.

Finally, variables can be defined within the module to allow the user to set them before running the module via the command line. Each command-line argument should correspond to a variable at the top of the module, which is then referenced in the appropriate locations throughout the script. Since the variables are defined before each module, the name-space between modules does not need to be maintained. However, for consistency, it is best to select variable names that are specific and unlikely to have shared meanings in other areas of the pipeline.

Data
----
scriptuit comes with a few command-line interfaces. These interfaces rely on a basic folder structure:

    /`SCRIPTUIT_DATA`
        /EXPERIMENTS
            /SUBJECTS
                /MODE
                    /SESS

**EXPERIMENTS**

This is a set of folders containing entire experiments. There are no important naming conventions, but it seems advisable (for consistency) to make the folder names all capitals, and short (e.g., `LINGASD` for 'language study on those with autism spectrum disorder').

**SUBJECTS**

Once again, these are simply folders with participant names. They follow no convention, but should be consistent for your own sake.

**MODE**

Image modality folders separate images of different kinds: related files originating from the same subject but with different meanings.

This allows you to seperate related data from a particular subject. For example, you might have physiological readings, an chest xray, and a CT scan from each participant. These files will need to be pre-processed individually, and then combined at some downstream stage. Assigning one image modaility to each file type will make it easy for you to write modules for each of these goals.

**SESS**

The session folders are used to separate data taken at different time points, or longitudinal data. They must begin with `SESS` and end with a zero-padded 2-digit number (e.g., `02`).

**RUN**

The run folders are used to separate data taken at the same time point. For example, repeats of the same data type. They must begin with `RUN` and end with a zero-padded 2-digit number (e.g., `02`).

Usage
-----
**scriptuit run**

This walks you through the construction of a pipeline for a single image modality within a single experiment. The command line interface allows you to chain together modules, keeping track of inputs/outputs, and the prerequisites for each module.

The modules used are determined by the current `SCRIPTUIT_MODULES` environment variable. You can use this to manage multiple parallel sets of modules. This is useful if you want to maintain a working legacy copy the scripts you used to a particular publication.

Each run of scriptuit is associated with an `ID`. This allows you to keep different streams of your pipeline seperate. This is useful if you are testing out multiple processing strategies on your data. `ID` is a variable made available within each of your modules, so you can put it somewhere in your output file names.

This generates a single master script with your modules chained together in order after you issue the stop command. This master script can be used to generate full rendered scripts for each participant, or can be used to analyze your data.

**scriptuit clean**

Allows you to find and destroy files with a given prefix, for all, or some of your subjects.

**scriptuit help**

Prints the help for the selected module.

**sit-folder**

This simple tool will help you generate folders properly-formatted for scriptuit. It is run on a per-subject basis, but a clever user could manually duplicate a single folder structure for as many participants as needed. These folders will automatically be generated in the designated working directory.

**epi-queue**

scriptuit can be used to generate a `proclist`, a list of the rendered scripts for each participant. This proclist can be run manually, if desired, but can also be submitted to a queue.
