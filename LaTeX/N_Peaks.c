#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(int argc, const char* argv [])
{
    srand(time(NULL));
    const int N = 200;
    const int X_MAX = 750;

    for (int i = 0; i < N; ++ i)
    {
        int x = 110 + i * (rand() % 5) + (rand() % 4);
        float y = 1.0 + ((rand() % 20) / 10.0);
        if (x > X_MAX)
        {
            continue;
        }
        if (x > 550)
        {
            y *= 6.5;
        }
        printf("%d/%.1f", x, y);
        if (i + 1 < N)
        {
            printf(", ");
        }
    }
    puts("");

    return 0;
}
