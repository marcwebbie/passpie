## Common issues

#### GPG not installed. https://www.gnupg.org/

You don't have gpg installed or it is not working as expected

Make sure you have [gpg](https://www.gnupg.org/) installed:

Ubuntu:

```
sudo apt-get install gpg
```

OSX:

```
brew install gpg
```

#### xclip or xsel not installed

You don't have *copy to clipboard* support by default on some linux distributions.

Ubuntu:

```
sudo apt-get install xclip
```

#### passpie init hangs

Sometimes it takes a long time because of entropy on the host machine. It was noticed a long time on an ubuntu server(even more if it is a virtual machine). You could try using `haveged` to generate enough entropy.

On ubuntu:

```
sudo apt-get install haveged
```
