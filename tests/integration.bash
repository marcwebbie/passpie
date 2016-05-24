set -e

source ~/.virtualenvs/passpie/bin/activate
PASSPIE_TEMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir')
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

# remove
passpie remove foo+test5@bar --yes
passpie remove barz --yes

# search
passpie search f
passpie search fo
passpie search foo
passpie search bar

# reset
passpie --passphrase=k reset --new-passphrase=kk
passpie --passphrase=kk copy foo@bar --to=stdout
