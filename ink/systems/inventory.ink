// ALL INVENTORY ITEMS MUST BE HERE
VAR inv_rusty_sword = false
VAR inv_old_sack = false
VAR inv_leather_armor = false

VAR eq_weapon = "none"
VAR eq_armor = "none"
VAR eq_outfit = "none"
VAR eq_hat = "none"
VAR eq_necklace = "none"
VAR eq_ring = "none"


=== inventory ===
Your gear:
Weapon: {eq_weapon}
Armor: {eq_armor}

+ {inv_rusty_sword and eq_weapon != "rusty_sword"} [Equip Rusty Sword (+2 STR)]
  ~ eq_weapon = "rusty_sword"
  You equip the sword.
  -> inventory

+ {inv_rusty_sword and eq_weapon == "rusty_sword"} [Unequip Rusty Sword]
  ~ eq_weapon = "none"
  You stow the sword.
  -> inventory

+ {inv_leather_armor and eq_armor != "leather_armor"} [Equip Leather Armor (+1 STR)]
  ~ eq_armor = "leather_armor"
  You buckle on the armor.
  -> inventory

+ {inv_leather_armor and eq_armor == "leather_armor"} [Unequip Leather Armor]
  ~ eq_armor = "none"
  You take off your armor.
  -> inventory

+ [Back]
  ->->