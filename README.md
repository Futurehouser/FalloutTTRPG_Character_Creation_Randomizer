<img width="1904" height="1032" alt="FOTTRPG_README" src="https://github.com/user-attachments/assets/a8a5331d-1650-4e5a-bcf5-275c8f8d9cff" />

## Download latest App Release [here](https://github.com/Futurehouser/FalloutTTRPG_Wasteland_Recruit/releases/latest)

(Windows: `WastelandRecruit.exe` · Android: `WastelandRecruit.apk`)

# Wasteland Recruit

**Wasteland Recruit** is a free, fan-made companion app for the **Fallout 2d20 tabletop roleplaying game**. It takes care of the slow parts of running a session (rolling up characters, building scavenging spots, looking up loot, running fights and tracking your party) so you can spend more time playing. It works on **Windows** (a single portable `.exe`, nothing to install) and **Android** (`.apk`), keeps everything on your device, and offers to update itself when a new version is released.

## What it does

Open the side menu (☰) to switch between the seven tools:

1. **Random Character**: one tap creates a complete level-1 character following the rulebook's character creation steps (origin, S.P.E.C.I.A.L., skills, perk, derived stats and equipment) and fills in the official character sheet. Each one gets a race-appropriate name and a personality quirk based on their stats. Save the sheet as an image, share it, or add the character to your saved list.
2. **Scavenging Location**: generates a ready-to-run place to loot, with its search test, difficulty and time, loot categories with min-max rolls, and possible inhabitants, obstacles, hazards and hidden stashes.
3. **Loot Roller**: pick an item category, enter your 2d20 result (or let the app roll), and see which item you found and how many combat dice to roll for the quantity. Every table can be edited so you can use the ones from your rulebook.
4. **Random FO76 Perk**: draws a random Fallout 76 perk card, with its image and the description of every rank, from fallout.wiki. Pick a saved character and it suggests a perk that fits their level, S.P.E.C.I.A.L. points, skills and the perks they already have.
5. **Create Character**: enter your own character's name, photo, S.P.E.C.I.A.L., skill ranks, perk cards, max HP, carry weight and notes. Characters without a photo get a cartoon portrait for their kind (human, ghoul, super mutant or robot).
6. **Saved Characters**: your party list. Open any profile to see its stats, edit it, **level it up**, get a perk suggestion, or delete it.
7. **Combat Assistant**: set up yourself, your weapon (fire rate, effects, ammo) and the enemies you face, and the app guides every turn: roll to hit, hit location, damage, damage effects, resistances and everyone's HP, for your attacks and the enemies'. Type in your own dice or tap *Roll for me*, mark enemies as dealt with, and finish with a victory screen that totals your XP, caps and loot.

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

The Android app is "WastelandRecruit.apk" (download link at the top). Just download that apk file to your android device and install it. Allow the installation anyways if your device doesn't trust the app.
