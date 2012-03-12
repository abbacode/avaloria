#HEADER
import random
from src.utils import create, search
from game.gamesrc.objects.world.items import Weapon, Armor, Potion

#CODE (Generate all items for loot tables)

#begin artifact item creation
storage = search.objects('storage', global_search=True)[0]
hammer = create.create_object(Weapon, key="An\'Karith's Hammer", location=storage, aliases=['epic_hammer'])
hammer.db.damage = "4d10"
hammer.db.attribute_bonuses = {'strength': 20, 'constitution': 15, 'dexterity': 15, 'intelligence': 10}
hammer.db.desc = "This giant two handed hammer looks impossible to lift, but is quite light in hand.  Runes are carved up and down the stone handle"
hammer.db.desc += " and hammer head.  They periodically flash a bright red."
hammer.db.value = 3490
hammer.db.item_level = "artifact"
hammer.db.weapon_type = 'hammer'
hammer.db.lootset = 'boss'

caller.msg("An\'Karith's hammer created, id: %s" % hammer.dbref)

aot = create.create_object(Weapon, key="Arm of the Tyrant", location=storage, aliases=['epic_sword'])
aot.db.damage = "3d12"
aot.db.attribute_bonuses = {'strength': 25, 'constitution': 10, 'dexterity': 10, 'intelligence': 5}
aot.db.desc = "A giant two handed sword that looks near impossible to lift, though you do notice the presense of magical runes on the hilt."
aot.db.value = 4890
aot.db.item_level = "artifact"
aot.db.weapon_type = "sword"
aot.db.lootset = 'boss'

caller.msg("Arm of the Tyrant created, id: %s" % aot.dbref)
#begin rare weapon item creation

axe = create.create_object(Weapon, key="Bloodletter Axe", location=storage, aliases=['rare_axe'])
axe.db.damage = "2d8"
axe.db.attribute_bonuses = {'strength': 5, 'constitution': 5, 'intelligence': 0, 'dexterity': 5 }
axe.db.desc = "A ferocious looking axe, the blade having a layer of dried blood caked on to it."
axe.db.value = 500
axe.db.item_level = "rare"
axe.db.weapon_type = "axe"
axe.db.lootset = "miniboss;rare"

caller.msg("Bloodletter Axe Created, id: %s" % axe.dbref)

sword = create.create_object(Weapon, key="Masterforged Short Sword", location=storage, aliases=['rare_sword'])
sword.db.damage = "2d6"
sword.db.attribute_bonuses = { 'strength': 5, 'constitution': 2, 'dexterity': 0, 'intelligence': 0 }
sword.db.desc = "A master work short sword with an extremely sharp edge."
sword.db.value = 289
sword.db.item_level = "rare"
sword.db.weapon_type = "sword"
sword.db.lootset = "rare"

caller.msg("Masterforged Short Sword created, id: %s" % sword.dbref)

dagger = create.create_object(Weapon, key="Gut Ripper", location=storage, aliases=['rare', 'rare_dagger'])
dagger.db.damage = "2d4"
dagger.db.attribute_bonuses = { 'strength': 0, 'constitution': 4, 'dexterity': 3, 'intelligence': 0}
dagger.db.desc = "A small weapon with a deadly curved blade.  The blade glows faintly, pulsing gently."
dagger.db.value = 309
dagger.db.item_level = "rare"
dagger.db.weapon_type = "dagger"
dagger.db.lootset = "rare"

caller.msg("Gut Ripper created, id: %s" % dagger.dbref)

pa = create.create_object(Weapon, key="Heroic Polearm", location=storage, aliases=['rare', 'rare_polearm'])
pa.db.damage = "2d10"
pa.db.attribute_bonuses = { 'strength': 4, 'constitution': 3, 'dexterity': 0, 'intelligence': 0 }
pa.db.desc = "A large spear with a trident style tip that slightly glows gold in the sunlight."
pa.db.value = 330
pa.db.item_level = "rare"
pa.db.weapon_type = "polearm"
pa.db.lootset = "rare"

caller.msg("Heroic Polearm created, id: %s" % pa.dbref)

#begin common weapon item creation
sword = create.create_object(Weapon, key="Longsword of the Bear", location=storage, aliases=['uncommon_sword'])
sword.db.damage = "1d8"
sword.db.attribute_bonuses = { 'strength': 3, 'constitution': 3, 'dexterity': 0, 'intelligence': 0 }
sword.db.desc = "A typical looking longsword, however there is a bear symbol carved into the shaft of the blade."
sword.db.value = random.randrange(13, 39)
sword.db.item_level = "uncommon"
sword.db.weapon_type = "sword"
sword.db.lootset = "uncommon"

caller.msg("Longsword of the Bear create, id: %s" % sword.dbref)

#Merchant weapons creation
sword = create.create_object(Weapon, key="Longsword", location=storage, aliases=['storage_weapons'])
sword.db.damage = '1d8'
sword.db.attribute_bonuses = {'strength': 0, 'constitution': 0, 'dexterity': 0, 'intelligence': 0 }
sword.db.desc = "A normal, run of the mill longsword."
sword.db.value = random.randrange(2,6)
sword.db.item_level = "common"
sword.db.weapon_type = "sword"

mob_sword = create.create_object(Weapon, key="Cruel Blade", location=storage, aliases=['mob_weapons', 'mob_blade'])
mob_sword.db.damage = '1d8'
mob_sword.db.attribute_bonuses = {}
mob_sword.db.desc = "A typical sword used by the mean spirited denziens of Avaloria."
mob_sword.db.value = random.randrange(2,6)
mob_sword.db.item_level = 'common'
mob_sword.db.weapon_type = sword

