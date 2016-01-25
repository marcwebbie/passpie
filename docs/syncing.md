# Syncing Credentials With Google Drive or Dropbox

## Dropbox

With default path `~/.passpie` and a Dropbox shared directory on path `~/Dropbox`

```bash
mv ~/.passpie ~/Dropbox/passpie    # move passpie db to Dropbox
ln -s ~/Dropbox/passpie ~/.passpie # make a link to the db
```

## Google Drive

With default path `~/.passpie` and a Google Drive shared directory on path `~/GoogleDrive`

```bash
mv ~/.passpie ~/GoogleDrive/passpie   # move passpie db to Google Drive
ln -s ~/GoogleDrive/passpie ~.passpie # make a link to the db
```
