// hello.c
#include <windows.h>

// Função exportada que mostra "hello" e retorna uma mensagem
__declspec(dllexport) const char* run() {
    int ret = MessageBoxA(NULL, "hello", "hello", MB_OK | MB_ICONINFORMATION);
    if (ret == IDOK) {
        return "hello exibido com sucesso!";
    } else {
        return "Falha ao exibir hello.";
    }
}

// DLL entry point
BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD  ul_reason_for_call,
                      LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
        case DLL_PROCESS_ATTACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;
}
