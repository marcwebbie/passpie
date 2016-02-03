sudo apt-get update --fix-missing
sudo apt-get install gnupg xsel haveged

sudo cp -a /dev/urandom /dev/random

pip install -U setuptools
pip install -e .

# initializing
passpie init --force --passphrase s3cr3t

# adding
passpie add foo@example.com --random
passpie add foo2@example.com --random
passpie add bar@example.com --pattern "[a-z]{30}"
passpie add spam@example.com --copy --pattern "[a-z]{30}"

# updating
passpie update foo@example.com --comment "something"
passpie update foo2@example.com --name "example.org"
passpie update foo2@example.org --login "foo"
passpie update spam@example.com --password "p4ssw0rd"

# copying
passpie copy foo@example.com  --passphrase s3cr3t
passpie copy bar@example.com  --passphrase s3cr3t
passpie copy spam@example.com  --passphrase s3cr3t --to=stdout

# exporting
passpie export --passphrase s3cr3t passwords.txt

# removing
passpie remove -y foo@example.com

# status
passpie status --passphrase s3cr3t

# purging and importing
passpie purge -y
passpie import passwords.txt
passpie

passpie purge -y
passpie import --cols ",,login,password,name,comment" examples/keepass.csv
passpie

passpie purge -y
passpie import --cols "name,login,password,,comment"  examples/lastpass.csv
passpie

# logging
passpie log

# completion
passpie complete bash
passpie complete fish
passpie complete zsh

# config
passpie config global
passpie config local
passpie config current
passpie config

# remote databases
passpie -D https://github.com/marcwebbie/passpiedb.git
passpie -D https://github.com/marcwebbie/passpiedb.git copy banks/mutuel
