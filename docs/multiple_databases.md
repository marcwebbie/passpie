# Multiple databases

Sometimes it is useful to have multiple databases with different passphrases for higher security. This can be done using `-D` or `--database` option.

## Creating databases

```bash
passpie -D ~/credentials/personal init
passpie -D ~/credentials/work init
passpie -D ~/credentials/junk init
```

## Adding passwords to specific database

```bash
passpie -D ~/credentials/personal add johnd@github.com --random
passpie -D ~/credentials/work add john.doe@example.com --random
passpie -D ~/credentials/junk add fake@example.com --random
```

## Listing passwords from specific database

```bash
$ passpie -D ~/databases/junk
===========  =======  ==========  =========
Name         Login    Password    Comment
===========  =======  ==========  =========
example.com  fake     *****
===========  =======  ==========  =========
```
