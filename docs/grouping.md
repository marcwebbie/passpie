# Grouping Credentials

## Grouping credentials by name

Passpie credentials handles multiple logins for each name which groups credentials by name:

```bash
# add some credentials
passpie add jonh@example.com --comment "Jonh main mail" --random
passpie add doe@example.com --comment "No comment" --random
```

Listing credentials:

```bash
$ passpie
===========  =======  ==========  ===============
name         login    password    comment
===========  =======  ==========  ===============
example.com  doe      *****       No comment
example.com  jonh     *****       Jonh main email
===========  =======  ==========  ===============
```

### Subgroups

Fullname syntax supports subgrouping of credentials by name

```
passpie add foo@opensource/github.com --random
passpie add foo@opensource/python.org --random
passpie add foo@opensource/bitbucket.org --random
passpie add foo@opensource/npm.org --random
```

Listing credentials:

```
$ passpie
========================  =======  ==========  =========
Name                      Login    Password    Comment
========================  =======  ==========  =========
opensource/bitbucket.org  foo      *****
opensource/github.com     foo      *****
opensource/npm.org        foo      *****
opensource/python.org     foo      *****
========================  =======  ==========  =========
```
