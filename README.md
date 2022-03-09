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
 2. Request an installation id and key from https://bitwarden.com/host/

 3. Edit the Vagrantfile in ./vagrant-box/ with the following information:
   - **Installation id**
   - **Installation key**

 4. At the root of your repository's copy, type:

    ```
    cd vagrant-box
    vagrant up
    ```

    This step can take a while, since a new Ubuntu virtual machine will be created. At the end of this step, this command will open a new virtual machine with Ubuntu installed.

 5. In the new virtual machine, login with the following credentials:

    - **Login:** vagrant
    - **Password:** vagrant

 6. Open a new terminal in the virtual machine. You can do this by pressing `ALT+F2` and writing the command `gnome-terminal`. Alternatively, you can right-click in the desktop and select the option _Open in Terminal_.

 7. From the terminal, run the following command:
    ```
    google-chrome --password-store=basic --allow-insecure-localhost "localhost"
    ```
    And create an account through the UI. The details of this account should be saved as they will be used later on.
    (This account is only stored in the local BitWarden server's vault)

 8. From the terminal, run the following command:
   ```
   cd  /home/vagrant/passcert/memdump-tests/
   ```
 9. Edit the sampleconfig.ini file with the following information:
   - E-mail address of the BitWarden account created in step 7
   - Password of the BitWarden account created in step 7
   - The desired amount of tests to be performed under "numberOfTests" (default is 5 tests).
   - (OPTIONAL) The directory where the memory dumps will be stored (if left empty, the current working directory will be used instead)

 10. Rename the file to "config.ini" (without quotation marks)

 11. From the terminal, run the following command:

     ```
     mkdir /home/vagrant/passcert/memdump-tests/memdumps
     cd /home/vagrant/passcert/memdump-tests/memdumps
     python3 /home/vagrant/passcert/memdump-tests/runLinux.py /home/vagrant/passcert/bw-browser-v1.55/build/ /home/vagrant/passcert/bw-browser-child-component/build/ /home/vagrant/passcert/bw-browser-no-child-component/build/
     ```

Since this will interact with the user interface, leave it to run without interfering. Do not use your keyboard, mouse, etc. until the message `"ALL TESTS DONE."` is displayed in the terminal.