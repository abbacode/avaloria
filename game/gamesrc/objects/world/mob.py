import random
from collections import deque
from src.utils import create
from game.gamesrc.objects.baseobjects import Object

class Mob(Object):
    """
    Class definition of a mobile object in the world (typically something 
    hunt.  But who knows, maybe it wil hunt you.
    
    ratings:
        'average': an average level of competence and difficulty.  A very
         typical encounter.
        'strong': an above average level of competence and difficulty.  A
         semi-tough fight.
        'hero': a very skilled level of competence and difficulty. A hard
         fight, but not un-doable.
        'demi-god': exteremely compentent and difficulty.  While a high
         level character could kill this, it would be VERY hard.
        'godlike': Near impossible to kill for all but the very highest
         level characters

    follow list:  this is a list that can be used to track down characters if they flee.
    """
    def at_object_creation(self):
        blackhole = self.search("blackhole", global_search=True)
        self.home = blackhole
        self.db.desc = "Some sort of creature."
        self.db.attributes = { 'level': 1, 'strength': 5, 'constitution': 5, 'dexterity': 5, 'intelligence': 5 }
        attributes = self.db.attributes
        attributes['temp_strength'] = attributes['strength']
        attributes['temp_dexterity'] = attributes['dexterity']
        attributes['health'] = attributes['constitution'] * 2
        attributes['temp_health'] = attributes['health']
        attributes['mana'] = attributes['intelligence'] * 2
        attributes['temp_mana'] = attributes['mana']
        attributes['armor_rating'] = (attributes['dexterity'] / 5) + 6
        attributes['attack_rating'] = attributes['strength'] / 5
        attributes['experience_made'] = 0
        attributes['expereince_needed'] = 200
        attributes['total_ex_made'] = 0
        self.db.equipment = { 'weapon': None, 'armor': None } 
        self.db.combat_queue = deque([])
        attributes['exp_award'] = None #exp awarded if killed
        attributes['gold'] = None
        self.aliases = ['mob']
        self.db.mob_type = None
        self.db.attributes = attributes
        self.db.combat_type = 'brute'
        self.db.corpse = False
        self.db.in_combat = False
        self.db.reanimate = False
        self.db.reanimator = False
        self.db.skills = []
        self.db.spells = []
        self.db.threat = {}
        self.db.should_update = True
        self.db.follow_list = []# a list of people to track down and kill
        self.db.rating = 'average' #A rating that dictates loot levels
        self.locks.add("get:none()")#we dont want folks picking us up and walking away
        #effect_manager = create.create_object("game.gamesrc.objects.world.spells.EffectManager", key = "%s_effect_manager" % self.name, location=self)
        #effect_manager.db.model = self
        #self.db.effect_manager = effect_manager
        #self.generate_level()
        self.generate_rewards()
        self.generate_stats()
        self.generate_physical_loot()
        self.update_stats()
        #self.scripts.add("game.gamesrc.scripts.world_scripts.mob_state_scripts.MobSentinel")
        
    def at_desc(self, looker):
        half_health = self.db.attributes['health'] / 2
        quarter_health = self.db.attributes['health'] / 4
        if self.db.attributes['temp_health'] <= quarter_health:
            looker.msg("%s is near death." % self.name)
        elif self.db.attributes['temp_health'] <= half_health:
            looker.msg("%s looks quite bloodied and beaten." % self.name)
        else:
            looker.msg("%s looks healthy and ready to fight!" % self.name)
        
    def at_inspect(self,looker):
        if self.db.corpse is True:
            m = "{bThis is just a corpse, it is not going to harm you, cause its already dead.{n"
            looker.msg(m)
        elif 'average' in self.db.rating:
            level_diff = int(self.db.attributes['level']) - int(looker.db.attributes['level'])
            if level_diff > 10:
                m = "{r%s would probably wipe the floor with you, it is much higher than you in level.{n" % self.name
                looker.msg(m)
            elif level_diff >= 6:
                m = "{y%s would be quite a challenge, but you should be able to take it down.{n" % self.name
                looker.msg(m)
            elif level_diff >=3:
                m = "{b%s may pose some challenge, but should be fairly easy to take down alone.{n" %self.name
                looker.msg(m)
            elif level_diff == 0:
                m = "{W%s should be an easy enough kill. Sweep the leg!{n" % self.name
                looker.msg(m)
            elif level_diff < 0:
                m = "{w%s would almost be a waste of your time.{n" % self.name
                looker.msg(m)
        elif 'strong' in self.db.rating:
            level_diff = self.db.attributes['level'] - looker.db.attributes['level']
            if level_diff > 10:
                m = "{r%s would probably wipe the floor with you, it is much higher than you in level.{n" % self.name
                looker.msg(m)
            elif level_diff >= 6:
                m = "{y%s would be quite a challenge, but you should be able to take it down.{n" % self.name
                looker.msg(m)
            elif level_diff >=3:
                m = "{b%s may pose some challenge, but should be fairly easy to take down alone.{n" % self.name
                looker.msg(m)
            elif level_diff == 0:
                m = "{W%s should be an easy enough kill. Sweep the leg!{n" % self.name
                looker.msg(m)
            elif level_diff < 0:
                m = "{w%s would almost be a waste of your time.{n" % self.name
                looker.msg(m)
        elif 'hero' in self.db.rating:
            level_diff = self.db.attributes['level'] - looker.db.attributes['level']
            if level_diff > 10:
                m = "{r%s would probably wipe the floor with you, it is much higher than you in level." % self.name
                looker.msg(m)
            elif level_diff >= 6:
                m = "{y%s would be very challenging, but you should be able to take it down.{n" % self.name
                looker.msg(m)
            elif level_diff >=3:
                m = "{b%s may pose some challenge, but should be able to be taken down alone.{n" %self.name
                looker.msg(m)
            elif level_diff == 0:
                m = "{W%s should be an equal, but tough match for you{n" % self.name
                looker.msg(m)
            elif level_diff < 0:
                m = "{w%s would almost be a waste of your time.{r" % self.name
                looker.msg(m)
        elif 'demi-god' in self.db.rating:
            m = "{r%s looks like it would be incredibly difficult to defeat. It would take everything you have in you.{n" % self.key
            looker.msg(m)
        elif 'god' in self.db.rating:
            m = "{r%s would wipe the floor with you. Find friends.{n" % self.key
            looker.msg(m)

    def death(self):
        self.db.pre_death_desc = self.db.desc
        self.db.pre_death_name = self.name
        self.db.desc = "A dead %s." % self.key
        self.key = "{rCorpse of %s{n" % self.key
        self.aliases = ['corpse', 'Corpse of %s' % self.key, self.key.lower()]
        self.db.lootable = True
        if self.db.reanimator:
            self.db.reanimate = True
        self.db.corpse = True
        self.db.in_combat = False
        #self.scripts.validate()
    
    def reanimate(self):
        attributes = self.db.attributes
        self.db.corpse = False
        self.db.lootable = False
        self.db.reanimate = False
        self.db.desc = self.db.pre_death_desc
        self.key = self.db.pre_death_name
        attributes['temp_health'] = attributes['health']
        attributes['temp_mana'] = attributes['mana']
        self.db.attributes = attributes

    def initiative_roll(self):
        roll = random.randrange(1,20)
        initiative_roll = roll +  self.db.attributes['attack_rating'] 
        return initiative_roll

    def attack_roll(self):
        roll = random.randrange(1,20)
        attack_roll = roll + self.db.attributes['attack_rating']
        return attack_roll

    def begin_attack(self, target):
        self.db.target = target
        target.scripts.add("game.gamesrc.scripts.world_scripts.combat_scripts.InCombatState")
        #ddself.scripts.add("game.gamesrc.scripts.world_scripts.mob_state_scripts.%s" % self.db.combat_type.title())

    def get_damage(self):
        """
        We try to get weapon dmg, if that is none then we default to our fists
        for 1d4 damage. Also check for a damage bonus and add it in if it is
        present.
        """
        attributes = self.db.attributes
        if self.db.equipment['weapon'] is not None:
            weapon = self.db.equipment['weapon']
            damage = weapon.damage.split('d')
            damage[0] = int(damage[0])
            damage[1] = int(damage[1])
            if damage[0] == 1:
                damage_roll = random.randrange(damage[0], damage[1])
            else:
                damage_roll = random.randrange(damage[0],(damage[1] *2))
        else:
            damage_roll = random.randrange(1,4)
        return damage_roll

    def take_damage(self,damage):
        attributes = self.db.attributes
        attributes['temp_health'] = int(attributes['temp_health']) - damage
        self.db.attributes = attributes
        return

    def update_stats(self):
        attributes = self.db.attributes
        attributes['health'] = (attributes['constitution'] * 2)
        attributes['mana'] = (attributes['intelligence'] * 2)
        attributes['attack_rating'] = (attributes['strength'] / 5)
        attributes['armor_rating'] = (attributes['dexterity'] / 5) + 6
        attributes['temp_health'] = attributes['health']
        attributes['temp_mana'] = attributes['mana']
        attributes['temp_strength'] = attributes['strength']
        attributes['temp_dexterity'] = attributes['dexterity']
        attributes['temp_armor_rating'] = attributes['armor_rating']
        attributes['temp_attack_rating'] = attributes['attack_rating']
        self.db.attributes = attributes
    
    def generate_level(self):
        #testing purposes only, never should really be used unless you want 
        #total random mobs
        attributes = self.db.attributes
        rn = random.randrange(1,60)
        attributes['level'] = rn
        ratings = ['average', 'strong', 'hero', 'demi-god', 'god']
        self.db.rating = random.choice(ratings)
        self.db.attributes = attributes

    def generate_skillset(self):
        skills = self.db.skills
        if 'brute' in self.db.combat_type:
            #self.scripts.add("game.gamesrc.scripts.world_scripts.mob_state_scripts.Kos")
            if self.db.equipment['weapon'] is not None:
                strike = create.create_object("game.gamesrc.objects.world.skills.Strike", key='strike', aliases=['mob_skills'])
                strike.db.character = self
                skills.append(strike)
            kick = create.create_object("game.gamesrc.objects.world.skills.Kick", key='kick', aliases=['mob_skills'])
            kick.db.character = self
            skills.append(kick)
            self.db.skills = skills
        elif 'caster' in self.db.combat_type:
            pass
        elif 'healer' in self.db.combat_type:
            spells = self.db.spells
            heal = create.create_object("game.gamesrc.objects.world.spells.Heal", key='Heal')
            spells.append(heal)
            self.db.spells = spells
        elif 'tank' in self.db.combat_type:
            pass
        elif 'dps' in self.db.combat_type:
            pass
        elif 'ranged_dps' in self.db.combat_type:
            pass 
            
            
    def generate_physical_loot(self):
        if self.db.boss_mob is True:
            loot_generator = create.create_object("game.gamesrc.objects.world.generators.LootGenerator")
            loot_item = loot_generator.create_rare_lootset()
            loot_item.move_to(self, quiet=True)
            loot_generator.delete()
            return

        rn = random.random()
        if self.db.rating in 'hero':
            if rn < 0.25:
                num_of_items = random.randrange(1,2)
                loot_generator = create.create_object("game.gamesrc.objects.world.generators.LootGenerator")
                loot = loot_generator.create_loot_set(loot_rating='rare', number_of_items=num_of_items, item_type='mixed')
                for item in loot:
                    item.move_to(self, quiet=True)
                loot_generator.delete()
                    
        if rn < 0.5:
            num_of_items = random.randrange(1,3)
            loot_generator = create.create_object("game.gamesrc.objects.world.generators.LootGenerator")
            ratings = ['uncommon', 'average', 'rare']
            rating = random.choice(ratings)
            loot = loot_generator.create_loot_set(loot_rating=rating, number_of_items=num_of_items, item_type='mixed')
            for item in loot:
                item.move_to(self, quiet=True)
            loot_generator.delete()

    def generate_rewards(self):
        attributes = self.db.attributes
        if 'average' in self.db.rating:
            gold = random.randrange(3,10)
            attributes['gold'] = gold
            exp = random.randrange(2,9)
            attributes['exp_award'] = exp + self.db.attributes['level']
        elif 'strong' in self.db.rating:
            gold = random.randrange(5,25)
            attributes['gold'] = gold
            exp = random.randrange(7,24)
            attributes['exp_award'] = exp + self.db.attributes['level']
        elif 'hero' in self.db.rating:
            gold = random.randrange(15,60)
            attributes['gold'] = gold
            exp = random.randrange(12,36)
            attributes['exp_award'] = exp + self.db.attributes['level']
        elif 'demi-god' in self.db.rating:
            gold = random.randrange(50,135)
            attributes['gold'] = gold
            exp = random.randrange(40,100)
            attributes['exp_award'] = exp + self.db.attributes['level']
        elif 'god' in self.db.rating:
            gold = random.randrange(100,450)
            attributes['gold'] = gold
            exp = random.randrange(100,600)
            attributes['exp_award'] = exp
        self.db.attributes = attributes
    
    def generate_stats(self):
        attributes = self.db.attributes
        if 'average' in self.db.rating:
            rn = random.randrange(3,18) #3d6 + level
            attributes['strength'] = rn + attributes['level']
            rn = random.randrange(3,18)
            attributes['dexterity'] = rn + attributes['level']
            rn = random.randrange(3,18) 
            attributes['intelligence'] = rn + attributes['level']
            rn = random.randrange(3,18)
            attributes['constitution'] = rn + attributes['level']
        elif 'strong' in self.db.rating:
            rn = random.randrange(4,24) #4d6 + level
            attributes['strength'] = rn + self.db.attributes['level']
            rn = random.randrange(4,24)
            attributes['dexterity'] = rn + self.db.attributes['level']
            rn = random.randrange(4,24)
            attributes['intelligence'] = rn + self.db.attributes['level']
            rn = random.randrange(4,24)
            attributes['constitution'] = rn + self.db.attributes['level']
        elif 'hero' in self.db.rating:
            rn = random.randrange(6,36) #6d6 + level
            attributes['strength'] = rn + self.db.attributes['level']
            rn = random.randrange(6,36)
            attributes['dexterity'] = rn + self.db.attributes['level']
            rn = random.randrange(6,36)
            attributes['intelligence'] = rn + self.db.attributes['level']
            rn = random.randrange(6,36)
            attributes['constitution'] = rn + self.db.attributes['level']
        elif 'demi-god' in self.db.rating:
            rn = random.randrange(12,72) #12d6
            attributes['strength'] = rn
            rn = random.randrange(12,72)
            attributes['dexterity'] = rn
            rn = random.randrange(12,72)
            attributes['intelligence'] = rn
            rn = random.randrange(12,72)
            attributes['constitution'] = rn
        elif 'god' in self.db.rating:
            rn = random.randrange(16,96)#16d6
            attributes['strength'] = rn
            rn = random.randrange(16,96)
            attributes['dexterity'] = rn
            rn = random.randrange(16,96)
            attributes['intelligence'] = rn
            rn = random.randrange(16,96)
            attributes['constitution'] = rn
        self.db.attributes = attributes 

    def irregular_action(self):
        mob_skills = self.db.skills
        mob_spells = self.db.spells
        player_map = self.location.db.player_map
        random_number = random.random()

        if self.db.in_combat is False:
            return

        if self.db.combat_type == 'brute':
            if random_number < .20:
                print "hit strike logic"
                [skill.on_use(self) for skill in mob_skills if 'strike' in skill.name]
            #for skill in mob_skills:
            #    if 'strike' in skill.name:
            #        skill.on_use(self.obj)
            elif random_number < .30:
                print "hit kick logic"
                [skill.on_use(self) for skill in mob_skills if 'kick' in skill.name]
            #for skill in mob_skills:
            #    if 'kick' in skill.name:
            #        skill.on_use(self.obj)
            else:
                return

    def kos_tick(self):
        if self.db.in_combat is True:
            return

        if self.db.corpse is True:
            return
        things_around_me = self.location.contents
        characters = self.db.characters
        if len(things_around_me) >= 1:
            characters = [thing for thing in things_around_me if thing.has_player is not False]
        else:
            return

        if len(characters) > 0:
            character = random.choice(characters)
            #make sure the character is still in the room.  there is a small chance the script
            #ran while they were, then they left after self.db.characters was compiled.
            character_check = self.search(character.name, global_search=False)
            if character_check is None:
                return
            chance = random.random()
            if chance < 0.10:
                if character:
                    if character.db.in_combat is True:
                        return
                    self.location.msg_contents("%s turns towards %s and readies their weapon." % (self.name, character.name))
                    character.db.target = self
                    self.begin_attack(character)
                    self.db.in_combat = True
            else:
                return


    def update(self):
        #effect_manager = self.obj.db.effect_manager
        #follow_list = self.obj.db.follow_list
        #effect_manager.check_effects()
        zone_manager = self.location.db.manager
        player_map = zone_manager.db.player_map
        
        if self.location.db.cell_number not in [ value for value in player_map.values()]:
            self.db.should_update = False
        if self.db.in_combat is True:
            #find the target, if none then get out of combat
            target = self.db.target
            if target is not None:
                if target.db.in_combat is True:
                    pass
                else:
                    self.db.in_combat = False
                    self.db.target = None
            else:
                self.db.in_combat = False
                return
        else:
            return
        
