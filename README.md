# The Bibites Mod Manager
The Bibites Mod Manager is the unofficial mod manager for The Bibite programmed in python (3.12) using tkinter. TBMM allows users to install mods with a simple gui instead off having to replace any dll manualy.
You can download and install mods with a few button clicks.
And can play both vanilla and modded with one install of The Bibites.

The final goal for TBMM is for it to be able to download and install any of the most popular mod and reskin types. Any other functionality secondary.

### Downloading TBMM
The release version can be downloaded here:<br>
https://github.com/MeltingDiamond/TBMM/releases/latest

For nightly version (most up to date version) you can click the links below:<br>
Windows: https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Windows.zip<br>
Linux:   https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Linux.zip<br>
Mac:     https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-macOS.zip

### Find any bugs please report them [here](https://github.com/MeltingDiamond/TBMM/issues) to help make TBMM better.

### Modifying and contributing
If you'd like to modify TBMM and share your changes, please fork the repository and submit a pull request with useful changes you've made. Your contributions will help improve the project, making it better for everyone. (This is based on trust.)

Anyone that contributes can get their name in the credits tab inside TBMM.

TBMM is licensed under the [GNU General Public License v3 (GPL-3.0)](/LICENSE.md), so you can freely modify and distribute it. However, any changes you make and distribute should also be shared under the same license.

Thank you for your contributions!

#### Building localy
Install python 3.12 (unless you have 3.10 or newer) and pip (no need if you already have)<br>
Download all the `.py` files, the `Images` folder and `build_requirements.txt` and place them in the same folder<br>
run `pip install -r build_requirements.txt` to install needed libraries/packages<br>
Now you have all requirements for running and building TBMM
To build TBMM run the command: `nuitka --onefile --windows-console-mode=disable --windows-icon-from-ico="Images\TBMM icon.ico" --include-data-dir="Images=Images" --enable-plugin=tk-inter "The Bibites Mod Manager.py"`<br>
This is the excact command that the auto build runs without `--assume-yes-for-downloads` (Only usefull in none interactive build scripts, like github actions).

## Next update
Start to make TBMM modular. Example would be moving all networking into one file then importing the correct function into main py file when needed. No new functionality will be added here. No major new functionality will be added.Around here TBMM will be officially open sourced. Check for newer version whenever you start TBMM

## Roadmap
### None version specific goals
- [x] Linux support 
- [x] Mac support (autobuilt in workflow)
- [ ] Make a document/wiki for how to use TBMM
- [ ] Show a prompt to download and setup correct version of The Bibites when choosing a mod. This will set it up in such a way that it is integrated into TBMMs files and can be reused for other mods made for the same version.
- [ ] Add check to mods that displays if they have compatebility issue with other mods.
- [ ] Dark mode???????
### The roadmap (-> indicates current released)
0.05 is the first alpha, which was filled with bugs.

0.06 will include automatically downloading bibites when you install a mod, hide mods that are not made for the selected game version and bugfixes.

-> 0.06.1 Rewrite the code for TBMM. This is to make it easier to work with TBMM in the future and no major new functionality will be added. Support for downloading mod data from dropbox will be added. TBMM is open sourced.

0.06.2 Start to make TBMM modular. Example would be moving all networking into one file then importing the correct function into main py file when needed. No new functionality will be added here. No major new functionality will be added.

0.06.3 TBMM will is mostly modularized.

When version 0.07 is released TBMM will support BepInEx mods and download BepInEx automatically to choosen location (Maybe install it automatically on the selected game path, will not be able to choose location if this is the case)

When version 0.08 is released TBMM will support mods that replaces the main dll but needs other files. Example of this is MoreMaterialsMod and reskin support will be added.

Version 0.09 will add support for at least 1 missing mod type if there are any.

When version 0.09 is finished TBMM should be completly modular, less chance of breaking and work better.

Version 0.1 will be the version that every mod is compatible and can be installed (dll replace, dll replace + other external files, BepInEx and BepInEx + other external files). I will delay 0.1 untill all mentioned mod types are supported. 

~0.7 and up I will make it open source and let the community help develop it further.<br>
After 0.1 there might be some ui updates to make TBMM look better and issues on the [issues page](https://github.com/MeltingDiamond/TBMM/issues) will be looked at and fixed.

Now there won't be any major version with planned features only bumps to the version whenever a new release happens. (New release happens whenever enough changes are done)

When 1.0 is released I hope it works like any other single game mod manager does and can be enjoyed by anyone of any skill level using any version that have mods.

I hope people will contibute both to TBMM directly and with mods and reskins that can be added to TBMM. Please enjoy TBMM.

### Running the .py file
Install python 3.10 (preferrably 3.12 newest) or newer and pip (no need if you already have)<br>
Download all the `.py` files, the `Images` folder and `requirements.txt` and place them in the same folder<br>
run `pip install -r requirements.txt` to install needed libraries/packages<br>
You can now run `The Bibites Mod Manager.py`