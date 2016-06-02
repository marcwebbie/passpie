set -e

source ~/.virtualenvs/passpie/bin/activate
PASSPIE_TEMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'passpietmp')
PASSPIE_EXPORT_TEMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'passpieexporttmp')
cp -R tests/database/ $PASSPIE_TEMPDIR
tree -a -I .git $PASSPIE_TEMPDIR
export PASSPIE_DATABASE=$PASSPIE_TEMPDIR
export PASSPIE_VERBOSE=3


# list
passpie
passpie list

# config
passpie config
passpie config current
passpie config global
passpie config local

# complete
passpie complete bash
passpie complete fish
passpie complete zsh

# add
passpie add foo+test1@bar --pattern="\d{2}"
passpie list
passpie add foo+test2@bar --random
passpie list
passpie add foo+test3@bar --comment "a comment" --random
passpie list
passpie add foo+test4@bar --password "a password"
passpie list
passpie add foo+test5@bar --pattern "[0-9]{5}[a-z]{5}[A-Z]{5}"
passpie list
passpie add foo+test6@bar --random
passpie list
passpie add foo+test6@bar --force --random
passpie list

# update
passpie update foo+test6@bar --name "barz"
passpie list
passpie update foo+test6@barz --login "fooz+test6"
passpie list
passpie update fooz+test6@barz --comment "updated comment"
passpie list
passpie update fooz+test6@barz --password "updated password"
passpie list

# copy
export PASSPIE_PASSPHRASE=k
passpie copy fooz+test6@barz
passpie copy fooz+test6@barz --to=clipboard
passpie copy fooz+test6@barz --to=stdout

# # remove
passpie remove foo+test5@bar --yes
passpie remove barz --yes

# # search
passpie search f
passpie search fo
passpie search foo
passpie search bar

# reset
unset PASSPIE_PASSPHRASE
passpie --passphrase=k reset --new-passphrase=s3cr3t
passpie --passphrase=s3cr3t copy foo+test4@bar --to=stdout
passpie list

# # log
passpie log

# export
passpie --passphrase s3cr3t export $PASSPIE_EXPORT_TEMPDIR/passpie.db

# import
passpie --passphrase s3cr3t import $PASSPIE_EXPORT_TEMPDIR/passpie.db
passpie list

# status
passpie  --passphrase s3cr3t status

# purge
passpie purge --yes

# import keepass
passpie import --cols ",,login,password,name,comment" examples/keepass.csv
passpie list

# import lastpass
passpie import --cols "name,login,password,,comment"  examples/lastpass.csv
passpie list

# logging
passpie log

# remote databases
passpie -D https://github.com/marcwebbie/passpiedb.git
passpie --passphrase s3cr3t -D https://github.com/marcwebbie/passpiedb.git copy banks/mutuel

# init
rm -rf /tmp/passpiedb
passpie --database /tmp/passpiedb --passphrase k init
passpie --database /tmp/passpiedb --passphrase k init --force
passpie --database /tmp/passpiedb --passphrase k init --force --no-git
passpie add foo@bar --random
passpie list
passpie --database /tmp/passpiedb --passphrase k init --force --recipient john.doe@example.com
