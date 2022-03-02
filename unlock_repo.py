#!/usr/bin/env python
"""Unlock the repo key using a pre-shared passphrase and use it to unlock the repo"""

import os
import sys
from shlex import split as shplit
from getpass import getpass
from subprocess import Popen
from subprocess import PIPE
from subprocess import check_output
from subprocess import CalledProcessError

try:
    keyfile = [
        keyfile
        for keyfile in [f"{dir}/.binder/key.asc" for dir in (".", "..")]
        if os.path.exists(keyfile)
    ][0]
except IndexError:
    print("Error: No keyfile found!", file=sys.stderr)
    sys.exit(1)

# Ensure we have user.name/email configured in case we have to stash/unstash
try:
    _ = check_output(shplit("git config --local user.name"), text=True)
    _ = check_output(shplit("git config --local user.email"), text=True)
except CalledProcessError:
    _ = check_output(shplit("git config --local user.name User"), text=True)
    _ = check_output(
        shplit("git config --local user.email user@example.com"), text=True
    )

unstash = lambda: None  # If there are no changes to stash, we don't need to unstash
if check_output(shplit("git stash"), text=True).startswith("Saved"):
    unstash = lambda: check_output(shplit("git stash pop"), text=True)  # for later...

gpg_proc = Popen(
    shplit(
        f"gpg --batch --quiet --yes"
        f" --passphrase {getpass('Enter secret: ')} --decrypt {keyfile}"
    ),
    stdout=PIPE,
)
git_proc = Popen(
    shplit("git crypt unlock -"),
    stdin=gpg_proc.stdout,
    stdout=PIPE,
    stderr=PIPE,
    text=True,
)
gpg_proc.stdout.close()  # Allow gpg_proc to receive a SIGPIPE if git_proc exits.
stdout, stderr = git_proc.communicate(timeout=3)

_ = unstash()  # if needed

if stderr:
    print("Error: Incorrect passphrase!", file=sys.stderr)
    sys.exit(1)
