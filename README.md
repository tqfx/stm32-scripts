# stm32 project initialization scripts

## Required tools

- [Java jre](https://www.oracle.com/java/technologies/javase-downloads.html)
- [STM32CubeMX](https://www.st.com/zh/development-tools/stm32cubemx.html)
- [Visual Studio Code](https://code.visualstudio.com/Download)

  It is recommended to use [msys2](https://msys2.org) to install the tool chain.

    ```bash
    pacman -S mingw-w64-x86_64-make
    pacman -S mingw-w64-x86_64-python
    pacman -S mingw-w64-x86_64-stlink
    pacman -S mingw-w64-x86_64-openocd
    pacman -S mingw-w64-x86_64-arm-none-eabi-toolchain
    ```

- [Make](http://gnuwin32.sourceforge.net/packages/make.htm)
- [Python](https://www.python.org/downloads/)
- [ST-Link-V2](https://www.st.com/zh/development-tools/st-link-v2.html#tools-software)
- [OpenOCD](https://openocd.org/)
- [GNU Arm Embedded Toolchain](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads)

> Don't forget to add the toolchain to the system environment variables.
