### Version control your database

Passpie by default will create a [git](https://git-scm.com/) repository on database initialization if `git` is available.

```bash
passpie init
```

To see the changes history, use passpie `log` command:

```bash
passpie log
```

example output:

```text
[13] Updated foo@bar
[12] Updated foo@bar
[11] Reset database
[10] Removed foozy@bar
[9] Updated hello@world
[8] Added hello@world
[7] Added foozy@bar
[6] Updated test@github
[5] Added foozy@bazzy
[4] Updated test@github
[3] Added foo@bar
[2] Added spam@egg
[1] Added test@github
[0] Initialized database
```

#### Going back to a previous version of the database changes.

If you want to go back to a previous version of the database history: `passpie --reset-to N` where N is the index of the change.

```
passpie log --reset-to 5
```

> *Attention*: this is an operation that destroys data. Use it with caution. It is equivalent to do `git reset --hard`

#### Initializing a git repository on an existing passpie database:

```bash
passpie log --init
```

or if you have multiple databases:

```bash
passpie -D other_database log --init
```

> This will create a git repository on passpie directory and create an initial commit `Initialized database`

#### Avoiding git initialization

If you don't want to create a git repository on the passpie database. Initialize passpie with `--no-git` flag:

```bash
passpie init --no-git
```
