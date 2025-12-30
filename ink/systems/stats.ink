VAR STR_BASE = 0
VAR CHA_BASE = 0
VAR WIT_BASE = 0


=== function WEAPON_STR_BONUS() ===
{ eq_weapon:
- "rusty_sword":    ~ return 2
- "iron_sword":     ~ return 4
- else:             ~ return 0
}

=== function ARMOR_STR_BONUS() ===
{ eq_armor:
- "leather_armor":  ~ return 1
- "chain_armor":    ~ return 2
- else:             ~ return 0
}

=== function STR() ===
~ return STR_BASE + WEAPON_STR_BONUS() + ARMOR_STR_BONUS()


=== function OUTFIT_CHA_BONUS() ===
{ eq_outfit:
- "old_sack":       ~ return -1
- else:             ~ return 0
}

=== function HAT_CHA_BONUS() ===
{ eq_hat:
- "top_hat":        ~ return 4
- else:             ~ return 0
}

=== function CHA() ===
~ return CHA_BASE + OUTFIT_CHA_BONUS() + HAT_CHA_BONUS()


=== function WIT_BONUS() ===
~ return 0

=== function WIT() ===
~ return WIT_BASE + WIT_BONUS()