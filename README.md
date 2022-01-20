# Cold Boot Attacks: Bitwarden's Browser Extension
This repository provides a vagrant box where automated cold boot attacks are performed on different versions of Bitwarden's browser extension. The goal is to enable easy replication of these attacks.

**Currrent status of development:** incomplete (in development)

## Installation
Provided that the dependencies below are satisfied, this artefact should work with any supported operating system. It was successfully tested in Ubuntu 20.04.3 LTS.

### Dependencies
 - [Vagrant](https://www.vagrantup.com/) (tested with version 2.2.19)
 - [VirtualBox]() (tested with version 6.1)

### Steps
If the dependencies above are satisfied, follow these steps:

 1. Clone this repository:

    ```
    git clone https://github.com/passcert-project/memdump-tests.git
    ```

 2. At the root of your repository's copy, type:

    ```
    vagrant up
    ```

    This step can take a while, since a new Ubuntu virtual machine will be created. At the end of this step, this command will open a new virtual machine with Ubuntu installed.

 3. In the new virtual machine, login with the following credentials:

    - **Login:** vagrant
    - **Password:** vagrant

 4. Open a new terminal in the virtual machine. You can do this by pressing `ALT+F2` and writing the command `gnome-terminal`.

 5. From the terminal, run the following command:

     ```
     python3 /home/vagrant/passcert/memdump-tests/runLinux.py
     ```

    Since this will interact with the user interface, leave it to run without interfering. Do not use your keyboard, mouse, etc. until the message `"ALL TESTS DONE."` is displayed in the terminal.