#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

bool is_prime(int n)
{
    if (n < 2)
        return false;
    for (int i = 2; i * i <= n; i++)
        if (n % i == 0)
            return false;
    return true;
}

int next_prime(int n)
{
    n++;
    while (!is_prime(n))
        n++;
    return n;
}

int int_to_char(int i)
{
    return 'a' + i % ('z' - 'a' + 1);
}

void lose()
{
    puts("Incorrect!");
    exit(EXIT_FAILURE);
}

void win()
{
    puts("Correct!");
    exit(EXIT_SUCCESS);
}

void main()
{
    printf("Enter password: ");
    char password[0x10];
    scanf("%16s", password);

    int n = 2;
    for (int i = 0; i < 0x10; i++)
    {
        if (password[i] != int_to_char(n))
            lose();
        n = next_prime(n);
    }
    win();
}
