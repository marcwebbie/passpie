# Diving into *fullname* syntax

Passpie credentials are referenced by `fullname`. fullname syntax handles login and name for credentials in one go for faster adding and querying of credentials.

## Structure of a fullname

Fullnames are composed of `login`@`name`. Login is optional. If you don't pass any login when adding new credentials, credential login will be replaced by a `_` character:

```bash
passpie add @banks/mybank --password 1234
passpie add @banks/myotherbank --password 5678
```

Listing credentials:

```bash
$ passpie
=================  =======  ==========  =========
Name               Login    Password    Comment
=================  =======  ==========  =========
banks/mybank       _        *****
banks/myotherbank  _        *****
=================  =======  ==========  =========
```

Since `login` is optional. You can query credentials using only name syntax, for example to update credential `@banks/mybank`:

```bash
passpie update @banks/mybank --random
```

Or even better, without using the `@` notation:

```bash
passpie update banks/mybank --random
```
