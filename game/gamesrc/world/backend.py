#HEADER
from src.utils import create, search

#CODE (create the backend room that contains all items in the game)
room_check = search("storage", global_search=True)
if room_check is None:
	caller.msg("Backend room exists, skipping.  Room id: %s"  % room_check.dbref)
	pass
else:
	room = create.create_object("game.gamesrc.objects.baseobjects.Room", key="storage", aliases=["items"])
	caller.msg("Backend Room created, id: %s" % room.dbref)

#CODE

preset_weapons = ['Sword of Truth', 'Blessed Hammer of An\'Karith', 'Axe of Ferocity', 'Arm of the Tyrant', 'Staff of Clarity',
					'Mace of the Druid King', 'Wizards Staff of Omen', 'Roderick\'s Claymore', ]
room = search("storage", global_search=True)
for weapon in preset_weapons:
	weapon = create.create_object("game.gamesrc.objects.world.items.Weapon", key=weapon, location=room)
	caller.msg("%s created!" % weapon.name)
	if 'Sword of Truth' in weapon:
		weapon.db.damage = "2d10"
		weapon.db.desc = "The sword's blade glimmers even when there is no light source.  It seeks evil."
		weapon.db.value = 1250
		weapon.db.item_level = "rare"
		weapon.db.slot = "weapon"
		weapon.db.weapon_type = "sword"
		weapon.db.attribute_bonuses = { 'str': 10, 'dex': 5, 'int': 1, 'con': 10 }
	elif 'Blessed Hammer of' in weapon:
		weapon.db.damage = "4d12"
		weapon.db.desc = "This giant two handed hammer looks impossible to lift, but is quite light in hand.  Runes are carved up and down the stone handle"
		weapon.db.desc += " and hammer head.  They periodically flash a bright red."
		weapon.db.value = 3490
		weapon.db.item_level = "artifact"
		weapon.db.weapon_type = 'hammer'
		weapon.db.attribute_bonuses = { 'str': 25, 'dex': 10, 'int': 15, 'con': 12, }
	elif 'Ferocity' in weapon:
		weapon.db.damage = "3d8"
		weapon.db.desc = "This is a large one-handed axe, orantely adorned with feathers below the axe-head.  The entire handle is wrapped in leather."
		weapon.db.value = 1390
		weapon.db.item_level = "rare"
		weapon.db.slot = "weapon"
		weapon.db.weapon_type = "axe"
		weapon.db.attribute_bonuses = {'str': 13, 'dex': 10, 'int': 3, 'con': 7}
	elif 'Tyrant' in weapon:
		weapon.db.damage = "4d8"
		weapon.db.desc = "This giant two handed sword almost looks near impossible to wield, however you can see magical runes carved into the hilt."
		weapon.db.value = 5000
		weapon.db.item_level = "artifact"
		weapon.db.slot = "weapon"
		weapon.db.weapon_type = "sword"
		weapon.db.atrribute_bonuses = {'str': 20, 'dex': 23, 'int': 10, 'con': 15}
	else:
		pass
	caller.msg("Attributes set.")
