<img width="1904" height="1032" alt="FOTTRPG_README" src="https://github.com/user-attachments/assets/a8a5331d-1650-4e5a-bcf5-275c8f8d9cff" />



App for Windows [**Windows**](https://github.com/Futurehouser/FalloutTTRPG_Character_Creation_Randomizer/releases/latest/download/WastelandRecruit.exe)

App for Mobile [**Mobile**](https://github.com/Futurehouser/FalloutTTRPG_Character_Creation_Randomizer/releases/latest/download/WastelandRecruit.apk)



# Rules from the Character Creation chapter from the Fallout 111 Table Top Roleplay Core Rulebook that the app follows:


Origin: one of Brotherhood Initiate, Ghoul, Super Mutant, Mister Handy, Survivor or Vault Dweller, with that origin’s special rules applied. That includes the super mutant attribute limits, the ghoul’s free Survival tag, the extra tag skill for Brotherhood and Vault Dwellers, and the Survivor’s two traits (or one trait plus a second perk).

S.P.E.C.I.A.L.: every attribute starts at 5, with 5 points to spend. It can lower an attribute to 4 to get an extra point, and nothing goes over the maximum.

Skills: 3 tag skills start at rank 2, then it spends 9 + INT skill points, with no skill above rank 3.

Perk: one perk whose requirements the character meets at level 1.

Derived stats: carry weight, defense, initiative, HP, melee damage, Luck points, and damage resistance for each body part from the worn armor.

Equipment: an equipment pack from the character’s origin, the items each tag skill grants, a trinket from the d20 table, and caps. Ammo amounts are already rolled with combat dice. The weapon and armor stats come from the Equipment chapter. For Mister Handy characters, it relabels the body-part boxes as the robot’s hit locations (optics, arms, thruster).

Names: made by mixing Fallout names for each race:

* Humans: first name plus surname (for example Boone Dashwood).
* Ghouls: sometimes get a nickname.
* Super mutants: single names, a title like “Uncle”, or two names blended together (for example Gracus).
* Robots: butler-style names with a title, like Sergeant or Miss, or a model number.

Gimmick: each character gets a nickname and a personality quirk based on their highest S.P.E.C.I.A.L. score, their lowest one and their perk. For example, Endurance 10 with low Charisma and the Pain Train perk gave “Unkillable”, who eats week-old mirelurk but whose small talk peaks at grunting, and who blows a train whistle before every charge. The quirk goes in the Perks \& Traits list. A “Wasteland Dossier” strip under the sheet holds the longer backstory and notes on the choices it made.

The source code lives in the `web` folder, which both apps share: gamedata.js has the rules data, generator.js builds the character and render.js fills in the sheet. `FalloutCharGen/desktop_app.py` is the Windows wrapper and `FalloutCharGenAndroid` holds the Android wrapper.

The Windows app is "WastelandRecruit.exe". You can move the exe anywhere, since it’s a single file. New characters are saved in a Fallout Characters folder next to wherever the exe is.

The Android app is "WastelandRecruit.apk" (link above). Just download that apk file to your android device and install it. Allow the installation anyways if your device doesn't trust the app.
