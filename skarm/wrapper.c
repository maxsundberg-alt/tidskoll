/* Tidskoll.app — startar skärmdumpsloopen (macOS).
 *
 * Varför en kompilerad app: behörigheten att spela in skärmen är knuten till
 * processens kodidentitet. Ett skalskript under launchd räknas som /bin/bash,
 * Apples egen fil, så behörigheten matchar aldrig och screencapture misslyckas
 * tyst. Det här programmet är appens huvudfil. Det lever kvar som den process
 * macOS ger behörigheten till, och startar skärmdumpsloopen som en barnprocess
 * som ärver den.
 *
 * Bygg:     cc -o Tidskoll.app/Contents/MacOS/tidskoll wrapper.c
 * Signera:  codesign -s - --force --identifier com.tidskoll.skarm Tidskoll.app
 * Bygg och signera en gång och ge behörighet efteråt. En ny signatur gör den
 * gamla behörigheten ogiltig.
 *
 * Bygger på wrapper.c i screenwatch-kit av Muhammad Ali (MIT-licens).
 */
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

int main(void) {
    char script[1024];
    snprintf(script, sizeof(script), "%s/tidskoll/bin/capture-loop.sh",
             getenv("HOME") ? getenv("HOME") : "");
    char *argv[] = {"/bin/bash", script, 0};
    for (;;) {
        pid_t pid;
        int status;
        if (posix_spawn(&pid, "/bin/bash", 0, 0, argv, environ) != 0)
            return 1;
        waitpid(pid, &status, 0);
        sleep(5); /* skärmdumpsloopen kraschade eller avslutades, starta om den */
    }
}
