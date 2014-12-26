mcv
===

MCV is a Python library that provides configuration management tools in
a simple package.

[![PyPI version](https://badge.fury.io/py/mcv.svg)](http://badge.fury.io/py/mcv) ![buildstatus](https://circleci.com/gh/framed-data/mcv.png?circle-token=0a1a9394ebb8bd9537203f1daf019edfbd4c2cd1)

MCV ships with modules for managing a variety of common functions:

- packages (e.g. `apt` and `pip`)
- users and groups
- files and directories
- git and github
- and more!


## Rationale

MCV is based on two ideas:

1. Real ops tasks demand no less than a full, first class programming
   language.  JSON and DSLs are empirically not expressive enough.  Bash
   is general but clunky and arcane.  By creating Python libraries, we
   provide a simple, powerful and community-accessible toolbox for
   getting things done.

2. Remote management is a myth.  Trying to execute commands over the
   wire forces us into impoverished latency and programming interfaces,
   e.g.  forcing everything to fit SSH shell commands.  The benefit of
   being able to write locally-running code far outweighs the cost of
   shipping that code to a box, especially since the management code
   need not change on every run.

Trying to define The One True System rarely succeeds.  Instead, a
library-based approach provides increasingly better tools so that
everyone can build the system they actually need, delegate functions
that are already well-defined and pre-solvable, and fill in any
remaining gaps using a solid general purpose programming language.
