<a name="top"></a>
* * *
# Reference Project
* * *

## Summary

Utility for installing and configuring the latest version of a reference project

Reference Project, VERSION **1.0**

* * *

## Contents

* [Getting Started](#getting-started)
* [Dependencies](#dependencies)
* [Details](#details)
* [Instructions](#instructions)
* [Help](#help)
* [Author & Copyright](#author--copyright)
* [License](#license)
* [Disclaimer](#disclaimer)


* * *

## Getting Started

See the following resources before getting started:

- Rkhunter [Project Site](http://rkhunter.sourceforge.net/) on Sourceforge
- Rkhunter Official [README](https://sourceforge.net/p/rkhunter/rkh_code/ci/master/tree/files/README)

[back to the top](#top)

* * *

## Dependencies

* Ubuntu, Ubuntu variants, 14.04
* Ubuntu, Ubuntu variants, 16.04+
* Redhat, Centos v7.0+
* [Amazon Linux](https://aws.amazon.com/amazon-linux-ami) 2017+

[back to the top](#top)

* * *

## Details

the following are details:

* **C Library**: `skdet`
    - required for specialized rootkit detection
    - compiles, installs

* **Uninstall Utility**
    - Installs uninstall utility in local config directory should you ever need to remove Rkhunter

* **Configuration File**
    - generates local configuration file required for uninstall


[back to the top](#top)

* * *

## Instructions

Run the installer from the cli via the following command:

```bash
    $ sudo sh rkhunter-install.sh
```

Installation directory is set using the `--layout` parameter:

```bash

    $ sudo sh rkhunter-install.sh --layout /usr    

        # install directory /usr/bin

```

[back to the top](#top)

* * *

## Help

To display the help menu:

```bash
    $ sh rkhunter-install.sh --help
```

[![help](./assets/help-menu.png)](https://rawgithub.com/fstab50/gensec/master/rkhunter/assets/help-menu.png)


To display help menu for the `--configure` option:

```bash
    $ sh rkhunter-install.sh --configure
```

[![help-configure](./assets/help-configure.png)](https://rawgithub.com/fstab50/gensec/master/rkhunter/assets/help-configure.png)

[back to the top](#top)

* * *

## Author & Copyright

All works contained herein copyrighted via below author unless work is explicitly noted by an alternate author.

* Copyright Blake Huber, All Rights Reserved.

[back to the top](#top)

* * *

## License

* Software contained in this repo is licensed under the [license agreement](./LICENSE.md).

[back to the top](#top)

* * *

## Disclaimer

*Code is provided "as is". No liability is assumed by either the code's originating author nor this repo's owner for their use at AWS or any other facility. Furthermore, running function code at AWS may incur monetary charges; in some cases, charges may be substantial. Charges are the sole responsibility of the account holder executing code obtained from this library.*

Additional terms may be found in the complete [license agreement](./LICENSE.md).

[back to the top](#top)

* * *
