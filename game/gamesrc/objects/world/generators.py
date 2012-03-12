import random
from src.utils import create,search
from game.gamesrc.objects.baseobjects import Object
from game.gamesrc.objects.world.dungeons import DungeonRoom
from game.gamesrc.objects import copyreader



class LootGenerator(Object):

    def at_object_creation(self):
        
        #Loot name banks
        self.db.avg_weapon_prefixes = ['Rusty', 'Iron', 'Steel', 'Wooden', 'Stone', 'Bronze', 'Battleworn', 'Used', 'Well Worn']
        self.db.unc_weapon_prefixes = ['Fine Steel', 'Fine Iron', 'Tempered Steel', 'Obsidian', 'Family', 'Fine Bronze', 'Gold Lined']
        self.db.rare_weapon_prefixes = ['Masterwork Steel', 'Masterwork Iron', 'Masterwork Steel', 
                                            'Diamond', 'Masterwork Bronze', 'Polished Obsidian', 'Masterwork Carbon Steel', 'Blessed', 'Lightbound' ]
        self.db.art_weapon_prefixes = ['Demon Forged', 'Angel Forged', 'God Forged', 'Demi-god Forged', 'Blessed', 'Cursed', 'Spellbound']
        self.db.weapon_choices = ['Longsword', 'Axe', 'Broadsword', 'Bastard Sword', 'Dagger', 'Short Sword', 'Polearm', ]
        #armor
        self.db.avg_armor_prefixes = ['Tattered', 'Worn', 'Battlescarred', 'Patched', 'Military Issue', 'Militia Issue', 'Ratty', 'Stained']
        self.db.unc_armor_prefixes = ['Finely Stitched', 'Family Heirloom', 'Standard', 'Finely Crafted', 'Good', 'Fitted']
        self.db.rare_armor_prefixes = ['Master Tailored', 'Masterwork', 'High Quality', 'Blessed', 'Light Touched', 'Darkness Touched', 'Spell Touched']
        self.db.art_armor_prefixes = ['God Touched', 'Demon Touched', 'Spell Woven', 'Light Blessed', 'Heavenly Crafted', 'Spell Touched']
        self.db.armor_choices = ['Leather', 'Chainmail', 'Plate', 'Studded Leather', 'Scalemail', 'Ringmail', 'Padded', 'Robe',
                                    'Half Plate', 'Mithril']
        self.db.level = 1
   
    def set_armor_type(self, armor, armortype):
        if 'plate' in armortype or 'Plate' in armortype:
            armor.db.armor_type = 'plate' 
        elif 'Mithril' in armortype:
            armor.db.armor_type = 'plate'
        elif 'Leather' in armortype or 'Padded' in armortype:
            armor.db.armor_type = 'leather'
        elif 'mail' in armortype or 'Mail' in armortype:
            armor.db.armor_type = 'mail'
        elif 'Cloth' in armortype or 'Robe' in armortype:
            armor.db.armor_type = 'cloth'
        return armor

    def set_weapon_type(self, weapon, weapontype):
        if 'sword' in weapontype or 'Sword' in weapontype:
            weapon.db.weapon_type = 'sword'
        elif 'axe' in weapontype or 'Axe' in weapontype:
            weapon.db.weapon_type = 'axe'
        elif 'dagger' in weapontype or 'Dagger' in weapontype:
            weapon.db.weapon_type = 'dagger'
        elif 'polearm' in weapontype or 'Polearm' in weapontype:
            weapon.db.weapon_type = 'polearm' 
        return weapon

    def set_armor_rating(self, armor):
        if 'average' in self.db.loot_rating:
            if 'plate' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(6,9)
            elif 'mail' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(3,6)
            elif 'leather' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(2,4)
            elif 'cloth' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(1,3)
        elif 'uncommon' in self.db.loot_rating:
            if 'plate' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(8,14)
            elif 'mail' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(3,9)
            elif 'leather' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(4,6)
            elif 'cloth' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(3,5)
        elif 'rare' in self.db.loot_rating:
            if 'plate' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(10,16)
            elif 'mail' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(5,11)
            elif 'leather' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(6,9)
            elif 'cloth' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(4,7)
        elif 'artifact' in self.db.loot_rating:
            if 'plate' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(15,20)
            elif 'mail' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(7,14)
            elif 'leather' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(8,11)
            elif 'cloth' in armor.db.armor_type:
                armor.db.armor_rating = random.randrange(5,10)
        return armor

    def set_weapon_damage(self, weapon):
        if 'sword' in weapon.db.weapon_type:
            weapon.db.damage = "1d8"
        elif 'axe' in weapon.db.weapon_type:
            weapon.db.damage = "1d10"
        elif 'dagger' in weapon.db.weapon_type:
            weapon.db.damage = "1d4"
        elif 'polearm' in weapon.db.weapon_type:
            weapon.db.damage = "1d12"
        return weapon

                 
    def create_loot_set(self, loot_rating, number_of_items, item_type):
        """
        This needs to be renamed.  This creates a fairly RANDOM lootset.  This is meant to be used
        within dungeons or other closely packed mob infested areas.  Just generate a loot generator
        on the mob, have it create a lootset, and you are golden.  By tweaking loot_rating and item
        type you can generate different things.  This is the method that uses the name banks declared
        at creation.
        """
        self.loot_rating = loot_rating
        self.number_of_items = number_of_items
        self.item_type = item_type
        loot_set = []

        if 'weapon' in self.item_type:  
            if 'average' in self.loot_rating:
                for i in range(number_of_items):
                    prefix = random.choice(self.db.avg_weapon_prefixes)
                    weapontype = random.choice(self.db.weapon_choices)
                    name = "%s %s" % (prefix, weapontype)
                    weapon = create.create_object("game.gamesrc.objects.world.items.Weapon", key="%s" % name)
                    weapon.db.value = random.randrange(1,10)
                    weapon.db.item_level = 'common'
                    weapon = self.set_weapon_type(weapon, weapontype)
                    weapon = self.set_weapon_damage(weapon)
                    desc = "%s looks to be a fairly common %s that most inhabitants of Avaloria would use." % (weapon.name, weapon.db.weapon_type)
                    weapon.desc = desc
                    loot_set.append(weapon)
                return loot_set
            elif 'uncommon' in self.loot_rating:
                bonus_choices = ['strength', 'constitution', 'dexterity', 'intelligence']
                bonus = random.choice(bonus_choices)
                for i in range(number_of_items):
                    prefix = random.choice(self.db.unc_weapon_prefixes)
                    weapontype = random.choice(self.db.weapon_choices)
                    name = "%s %s" % (prefix, weapontype)
                    weapon = create.create_object("game.gamesrc.objects.world.items.Weapon", key="%s" % name)
                    weapon.db.value = random.randrange(5,30)
                    weapon.db.item_level = 'uncommon'
                    weapon = self.set_weapon_type(weapon, weapontype)
                    weapon = self.set_weapon_damage(weapon)
                    weapon.db.attribute_bonuses = { '%s' % bonus: 1 }
                    desc = "The craftsmanship of %s is more refined than most of the other weapons you find." % weapon.name
                    desc += "\nThis is a well made %s." % weapon.db.weapon_type
                    weapon.desc = desc
                    loot_set.append(weapon)
                return loot_set
            elif 'rare' in self.loot_rating:
                for i in range(number_of_items):
                    prefix = random.choice(self.db.rare_weapon_prefixes)
                    weapontype = random.choice(self.db.weapon_choices)          
                    name = "%s %s" % (prefix, weapontype)
                    weapon = create.create_object("game.gamesrc.objects.world.items.Weapon", key="%s" % name)
                    weapon.db.value = random.randrange(15,70)
                    weapon.db.item_level = 'rare'
                    weapon = self.set_weapon_type(weapon, weapontype)
                    weapon = self.set_weapon_damage(weapon)
                    weapon.db.attribute_bonuses = { 'strength': 2, 'constitution': 2, 'intelligence': 2, 'dexterity': 2 }
                    loot_set.append(weapon)
                return loot_set
            elif 'artifact' in self.loot_rating:
                for i in range(number_of_items):
                    prefix = random.choice(self.db.art_weapon_prefixes)
                    weapontype = random.choice(self.db.weapon_choices)
                    name = "%s %s" % (prefix, weapontype)
                    weapon = create.create_object("game.gamesrc.objects.world.items.Weapon", key="%s" % name)
                    weapon.db.value = random.randrange(50,1000)
                    weapon.db.item_level = 'artifact'
                    weapon = self.set_weapon_type(weapon, weapontype)
                    weapon = self.set_weapon_damage(weapon)
                    loot_set.append(weapon)
                return loot_set
        elif 'armor' in self.item_type: 
            if 'average' in self.loot_rating:
                for i in range(number_of_items):
                    prefix = random.choice(self.db.avg_armor_prefixes)
                    armortype = random.choice(self.db.armor_choices)
                    name = "%s %s Armor" % (prefix, armortype)
                    armor = create.create_object("game.gamesrc.objects.world.items.Armor", key="%s" % name)
                    armor.db.value = random.randrange(1,10)
                    armor.db.item_level='common'
                    armor = self.set_armor_type(armor, armortype)
                    armor = self.set_armor_rating(armor)
                    desc = "%s is a very common, everyday piece of %s armor that people use to protect themselves." % (armor.name, armor.db.armor_type)
                    armor.desc = desc
                    loot_set.append(armor)
                return loot_set 
            elif 'uncommon' in self.loot_rating:
                for i in range(number_of_items):
                    prefix = random.choice(self.db.unc_armor_prefixes)
                    armortype = random.choice(self.db.armor_choices)
                    name = "%s %s Armor" % (prefix, armortype)
                    armor = create.create_object("game.gamesrc.objects.world.items.Armor", key="%s" % name)
                    armor.db.value = random.randrange(10,30)
                    armor.db.item_level='uncommon'
                    armor = self.set_armor_type(armor, armortype)
                    armor = self.set_armor_rating(armor)
                    desc = "As you inspect the %s, it is apparent it is not like the other hastily crafted armors you have seen." % armor.name
                    desc += "\nThis is a well made piece of %s armor" % armor.db.armor_type
                    armor.desc = desc
                    loot_set.append(armor)
                return loot_set 
            elif 'rare' in self.loot_rating:
                for i in range(number_of_items):
                    prefix = random.choice(self.db.rare_armor_prefixes)
                    armortype = random.choice(self.db.armor_choices)
                    name = "%s %s Armor" % (prefix, armortype)
                    armor = create.create_object("game.gamesrc.objects.world.items.Armor", key="%s" % name)
                    armor.db.value = random.randrange(45,150)
                    armor.db.item_level='rare'
                    armor = self.set_armor_type(armor, armortype)
                    armor = self.set_armor_rating(armor)
                    loot_set.append(armor)
                return loot_set 
            elif 'artifact' in self.loot_rating:
                for i in range(number_of_items):
                    prefix = random.choice(self.db.rare_armor_prefixes)
                    armortype = random.choice(self.db.armor_choices)
                    name = "%s %s Armor" % (prefix, armortype)
                    armor = create.create_object("game.gamesrc.objects.world.items.Armor", key="%s" % name)
                    armor.db.value = random.randrange(100,350)
                    armor.db.item_level='artifact'
                    armor = self.set_armor_type(armor, armortype)
                    armor = self.set_armor_rating(armor)
                    loot_set.append(armor)
                return loot_set 
        elif 'mixed' in self.item_type:
            loot_choices = ['weapon', 'potion', 'armor']
            for i in range(number_of_items):
                random_number = random.random()
                if random_number < .05:
                    choice = 'spellbook'
                elif random_number < 0.1:
                    choice = 'skillbook'
                else:
                    choice = random.choice(loot_choices)
                if 'weapon' in choice:                  
                    weapon = self.create_loot_set(loot_rating=self.loot_rating, number_of_items=1, item_type='weapon')
                    loot_set.append(weapon[0])
                elif 'armor' in choice:
                    armor = self.create_loot_set(loot_rating=self.loot_rating, number_of_items=1, item_type='armor')
                    loot_set.append(armor[0])
                elif 'potion' in choice:
                    potion_types = ['healing', 'mana_regen', 'buff']
                    effect = random.choice(potion_types)
                    if 'healing' in effect:
                        attribute_affected = 'hp'
                    elif 'mana_regen' in effect:
                        attribute_affected = 'mp'
                    elif 'buff' in effect:
                        buffs = ['hp', 'mp']
                        attribute_affected = random.choice(buffs)
                    decider = random.random()
                    if decider < 0.2:
                        level = 20
                    elif decider < 0.4 and decider > 0.2:
                        level = 10
                    else:
                        level = 1
                    potion = create.create_object("game.gamesrc.objects.world.items.Potion", key = "potion")
                    potion.db.level = level
                    potion.db.effect = effect
                    potion.db.attribute_affected = attribute_affected
                    potion.generate_item_stats()
                    loot_set.append(potion)                 
                elif 'skillbook' in choice:
                    skillbooks = [ 'kick', 'brawling', 'strike', 'toughness']
                    book = random.choice(skillbooks)
                    if 'kick' in book:
                        book = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", key="Training Manual: Kick")
                        book.db.skill = 'kick'
                        book.db.value = random.randrange(10,35)
                        book.db.level_requirement = 1
                    elif 'brawling' in book:
                        book = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", key="Training Manual: Brawling")
                        book.db.skill = 'brawling'
                        book.db.value = random.randrange(10,35)
                        book.db.level_requirement = 1
                    elif 'strike' in book:
                        book = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", key="Training Manual: Strike")
                        book.db.skill = 'strike'
                        book.db.value = random.randrange(10,35)
                        book.db.level_requirement = 3
                    elif 'toughness' in book:
                        book = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", key="Training Manual: Toughness")
                        book.db.skill = 'toughness'
                        book.db.value = random.randrange(10,35)
                        book.db.level_requirement = 5
                    loot_set.append(book)
                elif 'spellbook' in  choice:
                    spellbooks = ['fireball', 'mageshield', 'heal', 'strength of the bear']
                    book = random.choice(spellbooks)
                    if 'fireball' in book:
                        book = create.create_object("game.gamesrc.objects.world.spells.SpellBook", key="Spell Tome: Fireball")
                        book.db.spell = 'fireball'
                        book.db.value = random.randrange(30,65)
                        book.db.level_requirement = 1
                    elif 'mageshield' in book:
                        book = create.create_object("game.gamesrc.objects.world.spells.SpellBook", key="Spell Tome: Mage Shield")
                        book.db.spell = 'mageshield'
                        book.db.value = random.randrange(30,65)
                    elif 'heal' in book:
                        book = create.create_object("game.gamesrc.objects.world.spells.SpellBook", key="Spell Tome: Heal")
                        book.db.spell = 'heal'
                        book.db.value = random.randrange(30, 65)
                    elif 'strength of the bear' in book:
                        book = create.create_object("game.gamesrc.objects.world.spells.SpellBook", key="Spell Tome: Strength of the Bear")
                        book.db.spell = 'strength'
                        book.db.value = random.randrange(30,65)
                    elif 'magic missile' in book:
                        book = create.create_object("game.gamesrc.objects.world.spells.SpellBook", key="Spell Tome: Magic Missile")
                        book.db.spell = 'magic missile'
                        book.db.value = random.randrange(30,65)
                    loot_set.append(book)
            return loot_set


    def create_rare_lootset(self):
        storage = self.search("storage", global_search=True)
        items = storage.contents
        rare_items = []
        for item in items:
            try:
                if 'rare' in item.db.lootset:
                    rare_items.append(item)
            except (AttributeError, TypeError):
                continue
        rare_item_picked = random.choice(rare_items)
        rare_item_name = rare_item_picked.name #need this to change the key after a copy.
        rare_item_copy = rare_item_picked.copy()
        rare_item_copy.key = rare_item_name
        return rare_item_copy

    def create_artifact_lootset(self):
        storage = self.search("storage", global_search=True)
        items = storage.contents
        artifact_items = []
        for item in items:
            try:
                if 'artifact' in item.db.lootset:
                    artifact_items.append(item)
            except AttributeError, TypeError:
                continue
        art_item_picked = random.choice(artifact_items)
        art_item_name = art_item_picked.name
        art_item_copy = art_item_picked.copy()
        art_item_copy.key = art_item_name
        return art_item_copy
            
            
#end loot gen

#begin mob gen

class MobGenerator(Object):
    """
    This class generates a set of mob objects for characters to fight.
    Is used in combination with the Dungeon Generator that generates
    rooms and exits with a portal to the character's lair.
    """

    def at_object_creation(self):
        self.db.number_of_mobs = 1
        self.db.difficulty = 'average'
        self.db.dungeon_type = None
        self.db.mob_set = []

    def generate_mob_type(self):
        if 'crypt' in self.db.dungeon_type:
            self.db.ratings = ['average', 'strong']
            self.db.skeleton_prefixes = [ 'Charred', 'Darkbone', 'Earthen', 'Frail']
            self.db.zombie_prefixes = ['Headless', 'Rotting', 'Bloated', 'Crazed']
            self.db.ghoul_prefixes = ['Hungry', 'Blood-stained', 'Slobbering', 'Disgusting']
            self.db.apparition_prefixes = ['Shadowy', 'Smokey', 'Skeletal', 'Chillborn']
            self.db.average_mob_names = ['Skeleton', 'Zombie', 'Ghoul', 'Apparition' ]
            mob_name = random.choice(self.db.average_mob_names)
            if 'Skeleton' in mob_name:
                prefix = random.choice(self.db.skeleton_prefixes)
            elif 'Zombie' in mob_name:
                prefix = random.choice(self.db.zombie_prefixes)
            elif 'Ghoul' in mob_name:
                prefix = random.choice(self.db.ghoul_prefixes)
            elif 'Apparition' in mob_name:
                prefix = random.choice(self.db.apparition_prefixes)
            mob_name = "%s %s" % (prefix, mob_name)
            mob = create.create_object("game.gamesrc.objects.world.mob.Mob", key = "%s" % mob_name, location=self.location) 
            mob.aliases = ['mob_runner', 'irregular_runner', 'kill_crypt_mobs', 'crypt_mobs', 'kill_undead', 'kill_%s' % mob.name.lower()]
            try:
                mob.desc = copyreader.read_file("gamesrc/copy/mobs/%s_%s.txt" % (prefix.lower(), mob_name.lower()))
            except:
                mob.desc = "Placeholder, no desc written"
            mob.db.level = self.location.db.level
            mob.db.rating = random.choice(self.db.ratings)
            mob.db.is_kos = True
            mob.db.mob_type = 'undead'
        elif 'ruins' in self.db.dungeon_type:
            self.db.ratings = ['average', 'strong']
            self.db.spider_prefixes = [ 'Common', 'Large', 'Hulking', 'Behemoth' ]
            self.db.pigmy_prefixes = [ 'Small', 'Mature', 'Young']
            self.db.ancestral_spirit_prefixes = [ 'Ethereal', 'Shadowy', 'Lightbourne', 'Ancestral' ]
            self.db.average_mob_names = ['Spider', 'Pigmy', 'Spirit']
            mob_name_original = random.choice(self.db.average_mob_names)
            if 'Spider' in mob_name_original:
                prefix = random.choice(self.db.spider_prefixes)
            elif 'Pigmy' in mob_name_original:
                prefix = random.choice(self.db.pigmy_prefixes)
            elif 'Spirit' in mob_name_original:
                prefix = random.choice(self.db.ancestral_spirit_prefixes)
            mob_name = "%s %s" % (prefix, mob_name_original)
            mob = create.create_object("game.gamesrc.objects.world.mob.Mob", key="%s" % mob_name, location=self.location)
            mob.aliases = ['mob_runner', 'irregular_runner', 'ruins_mobs', 'kill_ruins_mobs', 'kill_%s' % mob_name_original.lower()]
            mob.db.level = self.location.db.level
            mob.db.rating = random.choice(self.db.ratings)
            mob.db.mob_type = '%s' % mob_name_original.lower()
        elif 'marshlands' in self.db.dungeon_type:
            self.db.ratings = ['average', 'strong', 'hero']
            self.db.slythain_prefixes = [ 'Young', 'Mature', 'Adolescent' ]
            self.db.slythain_suffixes = [ 'Marauder', 'Assassin', 'Hunter', 'Tracker', 'Guardian' ]
            self.db.grasswhip_prefixes = [ 'Young', 'Adult', 'Weathered', 'Juvenile' ]
            self.db.bearcat_prefixes = [ 'Matriarch', 'Patriarch', 'Juvenile', 'Young' ]
            self.db.mob_names = ['Bearcat','Slythain', 'Grasswhip' ]
            mob_name_original = random.choice(self.db.mob_names)
            if 'Slythain' in mob_name_original:
                prefix = random.choice(self.db.slythain_prefixes)
                suffix = random.choice(self.db.slythain_suffixes)
                mob_name = "%s Slythain %s" % (prefix, suffix)
                desc = copyreader.read_file("gamesrc/copy/mobs/%s_%s.txt" % (mob_name_original.lower(), suffix.lower()))
                deity = 'slyth'
            elif 'Grasswhip' in mob_name_original:
                prefix = random.choice(self.db.grasswhip_prefixes)
                mob_name = "%s Grasswhip" % prefix
                desc = copyreader.read_file("gamesrc/copy/mobs/%s_%s.txt" % (prefix.lower(), mob_name_original.lower()))
                deity = 'slyth'
            elif 'Bearcat' in mob_name_original:
                deity = 'warden'
                prefix = random.choice(self.db.bearcat_prefixes)
                mob_name = "%s Bearcat" % prefix
                desc = copyreader.read_file("gamesrc/copy/mobs/%s_%s.txt" % (prefix.lower(), mob_name_original.lower()))
            mob = create.create_object("game.gamesrc.objects.world.mob.Mob", key = "%s" % mob_name, location=self.location)
            mob.db.deity = deity
            mob.desc = desc
            mob.aliases = ['kill_%s' % deity, 'kill_%s' % mob_name.lower(), 'mob_runner', 'irregular_runner','kill_marshlands', 'kill_%s' % mob_name_original.lower(), 'marshlands_mobs']
            split = self.db.level.split(';')
            level = random.randrange(int(split[0]), int(split[1]))
            mob.db.attributes['level'] = level
            mob.db.rating = random.choice(self.db.ratings)
            mob.db.is_kos = True
            mob.db.mob_type = '%s' % mob_name_original.lower()
        rn = random.random()
        if rn <= .40:
            weapon = self.search('mob_blade', global_search=True, ignore_errors=True)[0]
            mob_weapon = weapon.copy()
            mob_weapon.name = weapon.name
            equipment = mob.db.equipment
            equipment['weapon'] = mob_weapon
            mob.db.equipment = equipment

        mob.generate_stats()
        mob.generate_skillset()
        mob.generate_rewards()
        mob.update_stats()
        return mob
            
    def generate_mob_set(self, number_of_mobs):
        mob_set = []
        for i in range(0, number_of_mobs):
            mob = self.generate_mob_type()
            mob_set.append(mob)
        return mob_set

    def generate_boss_mob(self):
        if 'crypt' in self.db.dungeon_type:
            self.db.boss_names = ['Skeletal Lich', 'Frostbourne Witch']
            boss_name = random.choice(self.db.boss_names)
            boss_mob = create.create_object("game.gamesrc.objects.world.mob.Mob", key="%s" % boss_name, location=self.location)
            boss_mob.aliases = ['boss_mob']
            boss_mob.db.level = self.location.db.level
            boss_mob.db.rating = 'hero'
            boss_mob.db.boss_mob = True
            boss_mob.generate_stats()
            boss_mob.generate_rewards()
            boss_mob.generate_physical_loot()
            boss_mob.generate_skillset()
            boss_mob.update_stats()
            return boss_mob
        if 'ruins' in self.db.dungeon_type:
            self.db.boss_names = ['Pygmy Lord', 'Ghastly Ghoul', 'Spider Queen']
            boss_name = random.choice(self.db.boss_names)
            boss_mob = create.create_object("game.gamesrc.objects.world.mob.Mob", key="%s" % boss_name, location=self.location)
            boss_mob.aliases = ['boss_mob']
            boss_mob.db.level = self.location.db.level
            boss_mob.db.rating = 'hero'
            boss_mob.db.boss_mob = True
            boss_mob.generate_stats()
            boss_mob.generate_rewards()
            boss_mob.generate_physical_loot()
            boss_mob.generate_skillset()
            boss_mob.update_stats()
            return boss_mob 
            
            
    

class DungeonGenerator(Object):
    """
    This generates dungeons and exits linking them together for the character to adeventure
    through. This also generates a Zone object to manage the rooms in the dungeon that is
    created.
    TODO: Add more door types, add more dungeon types.
    """
    def at_object_creation(self):
        self.db.dungeon_types = ['crypt', 'ruins']
        self.db.exit_types = ['Wooden Door', 'Small Crawlspace', 'Stairs leading down', 'Tunnel Opening', 
                                'Large Wooden Door', 'Heavy Stone Door', 'Large Iron Gate', 'Rotten Wooden Door']
        self.db.dungeon_type_picked = random.choice(self.db.dungeon_types)
        #self.db.manager_id = self.location
        self.db.level = 1
        self.db.number_of_rooms = random.randrange(2, 4)
        
    def generate_room_texts(self, room):
        """
        TODO: Add a whole lot more dungeon types
        """
        if 'crypt' in self.db.dungeon_type_picked:
            self.db.desc_choices = ['This dimly lit chamber smells of mold and mildew.  The walls seem to be crumbling, and a thick lair of dust lines the floor.', 'As you step into this room, you notice the walls have large murals depicted upon them.  Tributes to the old gods, most likely from rituals of death.', 'Sarcophigi line the walls and it feels as if an unseen force is watching your every move.  You can feel your cold sweat trickle down your neck.', 'It is so cold you can see your breath clearly when exhaled.  The chill penetrates down to your very bones.']
            room.db.desc = random.choice(self.db.desc_choices)
        elif 'ruins' in self.db.dungeon_type_picked:
            self.db.desc_choices = ['This room is very large, and has literally been carved out of the rock itself.  Outside your torch light is pitch black nothingness.  There is no sound that you can hear aside from your own breathing.  The walls that you can see have large murals painted all over them.  Obviously something lives in this dark, long forgotten place.', 'As you make your way through the cavernous dark, you come upon a small room.  The walls are intricately carved into patterns and shapes that you almost lose yourself in as you stare at them.']
            room.db.desc = random.choice(self.db.desc_choices)
        else:
            pass
   
    def generate_zone_manager(self):
        zone = create.create_object('game.gamesrc.objects.world.rooms.Zone', key="%s Zone Manager" % self.db.dungeon_type_picked.title()) 
        zone.db.zone_type = self.db.dungeon_type_picked
        mg = zone.db.mob_generator
        mg.db.dungeon_type = self.db.dungeon_type_picked 
        zone.db.mob_generator = mg
        zone.aliases = ['zone_runner']
        zone.db.zone_name = '%s' % self.db.dungeon_type_picked.title()
        zone.db.is_dungeon = True
        zone.db.quest_items = ['Deity Seal']
        self.db.zone = zone

    def update_zone_manager(self, zone):
        self.db.zone = zone
        
    def generate_rooms(self):
        """
        This generates the actual room objects of the dungeon
        TODO: Add cardinal direction to where exits point.
        """
        #is there already a dungeon built?
        manager = self.db.manager
        if len(manager.db.dungeon) >= 1:
            manager.delete_previous_dungeon()
            #we need to nuke to zone object as well so it re-creates itself on this use
            zone = self.db.zone
            zone.delete()
            self.db.zone = None

        #If we have no zone attribute, make a zone object and assign one.
        if not hasattr(self, 'zone'):
            self.generate_zone_manager()
            zone = self.db.zone
        #or if the zone attribute is None, create and assign on
        elif self.db.zone is None:
            self.generate_zone_manager()
            zone = self.db.zone
        else:
        #or just use whats there.
            zone = self.db.zone
        #grab the zone path map for the dungeon
        path_map = zone.db.path_map
            
        dungeon = []
        #first we build a list of rooms.
        for i in range(self.db.number_of_rooms):
            room = create.create_object("game.gamesrc.objects.world.dungeons.DungeonRoom", key = "%s - Room %s" % (self.db.dungeon_type_picked, i))
            self.generate_room_texts(room)
            room.db.level = self.db.level
            room.db.dungeon_type = self.db.dungeon_type_picked
            if i == self.db.number_of_rooms - 1:
                room.db.last_room = True
            else:
                room.db.last_room = False
            #add the script that spawns and watches the rooms treasure spawn (chests, loot caches and what not)
            room.scripts.add("game.gamesrc.scripts.world_scripts.dungeon_scripts.TreasureSpawner")
            room.db.manager = zone
            #add the room to the dungeon list of rooms
            dungeon.append(room)
            #add the cell to the path_map so the zone manager knows where to look for things.
            path_map['A%s' % i] = room
            #add a cell number to the dungeon room
            room.db.cell_number = 'A%s' % i
            if i > 0:
                room.aliases = ['%s_quest_item_spawn' % self.db.dungeon_type_picked]
        zone.db.path_map = path_map
        manager.db.dungeon = dungeon
        self.db.zone = zone
        #manually trigger zone_runner to spawn mobs
        zone_runner_script = search.scripts('zone_runner')[0]
        zone_runner_script.at_repeat() 

        i = 0   
        lair = self.search(self.location.db.lair_id, global_search=True)
        rooms = manager.db.dungeon
        for room in manager.db.dungeon:
            exit_name = random.choice(self.db.exit_types)
            if i != 0:
                #if not the first room
                previous_room = rooms[i - 1]
                destination_obj = previous_room
                #link to previous room
                exit = create.create_object("game.gamesrc.objects.baseobjects.Exit", key="Previous Room", location=room, destination=destination_obj)
                exit.aliases = [exit.key.lower(), 'prev', 'pr']
                exit_name = random.choice(self.db.exit_types)
                #link to the next room
                try:    
                    next_room = rooms[i + 1]
                except IndexError:
                    
                    return
                destination_obj = next_room
                exit2 = create.create_object("game.gamesrc.objects.baseobjects.Exit", key=exit_name, location=room, destination=destination_obj)
            else:
                #portal back home
                exit = create.create_object("game.gamesrc.objects.baseobjects.Exit", key="Glowing Red Portal", location=room, destination=lair)
                exit.aliases = [ 'portal', 'glowing portal', 'red portal' ]
                #portal to the dungeon
                entrance_to_dungeon = create.create_object("game.gamesrc.objects.baseobjects.Exit", key="Glowing Red Portal",
                                                                 location=lair, destination=room)
                entrance_to_dungeon.aliases = [ 'portal', 'glowing portal', 'red portal' ]
                next_room = rooms[1]
                exit_name = random.choice(self.db.exit_types)
                destination_obj = next_room
                next_room_exit = create.create_object("game.gamesrc.objects.baseobjects.Exit", key=exit_name, 
                                                            location=room, destination=destination_obj)
            i += 1

