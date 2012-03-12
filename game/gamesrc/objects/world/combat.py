import random, time
from collections import deque
from game.gamesrc.objects.baseobjects import Object

class CombatManager(Object):
    """
    This represents a combat management object, and it largely handles all
    combat related actions/results.  Currently, we only support a single target
    and no grouping on either side. This will likely change down the road.
    """

    def at_object_creation(self):
        self.attacker = None
        self.attacker_queue = []
        self.defender = None
        self.defender_queue = []
        self.max_actions = 4
    
    def generate_texts(self):
        """
        TODO: Add more texts.
        """
        self.missed_attacks_text = ["You try to hit %s but miss." % self.defender.key, 
                                        "As you bring your weapon down, it bounces off of %s's armor harmlessly" % self.defender.key,
                                        "You swing your weapon but miss mightily.", 
                                        "You try to clobber %s, but miss wildly." % self.defender.key]
        self.opponent_missed_attacks_text = ["%s misses you with their wild attack." % self.defender.key]
    
    def score_hit(self, who):
        if 'attacker' in who:
            damage_amount = self.attacker.get_damage()
            self.defender.take_damage(damage=damage_amount)
            self.attacker.msg("You deal {r%s{n damage to %s." % (damage_amount, self.defender.key ))
            """
            if self.defender.db.attributes['temp_health'] <= 0:
                self.attacker.msg("{bYou have defeated your foe!{n DEBUG: inside combat manager")
                self.attacker.msg_contents("%s has defeated %s" % (self.attacker.name, self.defender.name))
                self.attacker.award_exp(self.defender.db.attributes['exp_award'])
                self.check_quest_flags()
                self.defender.death()
                self.attacker.db.in_combat = False
                self.attacker.scripts.validate()
            """
            return
        else:
            damage_amount = self.defender.get_damage()
            self.attacker.take_damage(damage=damage_amount)
            self.attacker.msg("You take {r%s{n points of damage." % damage_amount)
            self.attacker.msg("{rHP: (%s/%s){n {bMP: (%s/%s){n" % (self.attacker.db.attributes['temp_health'], self.attacker.db.attributes['health'], 
                                        self.attacker.db.attributes['temp_mana'], self.attacker.db.attributes['mana']))
            if self.attacker.db.attributes['temp_health'] <= 0:
                self.attacker.msg("{rYou have been killed!")
                self.attacker.location.msg_contents("{r%s has be slain by %s!{n" % (self.attacker.name, self.defender.name), exclude=self)
                self.defender.db.target = None
                self.defender.db.in_combat = False
                self.attacker.death()   
            return

    def check_quest_flags(self):
        quest_log = self.attacker.db.quest_log
        quest_log.check_quest_flags(self.db.defender)
                     
    def score_miss(self, who):
        if 'attacker' in who:
            miss_text = random.choice(self.missed_attacks_text)
            self.attacker.msg(miss_text)
            return
        else:
            miss_text = random.choice(self.opponent_missed_attacks_text)
            self.attacker.msg(miss_text)
            return
        
    def process_action(self):
        atk_queue = self.attacker_queue
        def_queue = self.defender_queue
        
        atk_queue = deque(atk_queue)
        def_queue = deque(def_queue)
        try: 
            atk_action = atk_queue.popleft()
        except IndexError:
            atk_action = 'attack'
      
        try:
            def_action = def_queue.popleft()
        except IndexError:
            def_action = 'attack'
        
        if len(atk_queue) >= 2:
            self.db.current_action = atk_action
            self.db.next_action = atk_queue[0]
            self.db.second_action = atk_queue[1]

        self.attacker_queue = atk_queue
        self.defender_queue = def_queue
        self.defender.db.combat_queue = def_queue
        self.attacker.db.combat_queue = atk_queue
        
        #self.attacker.msg("{yYour Attack Queue: {g%s{n" % self.attacker_queue)
        self.attacker_initiative = self.attacker.initiative_roll()
        self.defender_initiative = self.defender.initiative_roll()
        if self.attacker_initiative > self.defender_initiative:
            if 'attack' in atk_action: 
                attack_roll = self.attacker.attack_roll()
                if attack_roll >= self.defender.db.attributes['armor_rating']:
                    if 'defend' in def_action:
                        self.attacker.msg("%s is in a defensive position, negating your attack." % self.defender.name)
                        return
                    elif 'attack' in def_action:
                        defender_attack_roll = self.defender.attack_roll()
                        if defender_attack_roll >= self.attacker.db.attributes['temp_armor_rating']:
                            self.score_hit(who='defender')
                        else:
                            self.score_miss(who='defender')                 
                    else:
                        pass
                        #do nothing    
                    self.score_hit(who="attacker")
                else:
                    self.score_miss(who="attacker")
            elif 'defend' in atk_action:
                self.attacker.msg("{bYou are in a defensive stance, negating any damage done.{n")
                return
                if 'attack' in def_action:
                    def_atk_roll = self.defender.attack_roll()
                    if def_atk_roll >= self.attacker.db.attributes['temp_armor_rating']:
                        self.score_hit(who="defender")
                    else:
                        self.score_miss(who="defender")
                elif 'defend' in def_action:
                    self.attacker.msg("{b%s and yourself seem to have defended at the same time, so you stare at each other viciously.{n" % self.defender.name)
            elif 'skill' in atk_action:
                split = atk_action.split(':')
                #self.attacker.msg("You prepare to use the skill: {g%s{n!" % split[1].title())
                #self.check_for_combo( )
                manager = self.attacker.db.skill_log
                character_skills = manager.db.skills
                if split[1] in character_skills.keys():
                    skill_obj = character_skills[split[1]]
                    skill_obj.on_use(caller=self.attacker)
                
            else:
                pass
        else:
            if 'attack' in def_action:
                attack_roll = self.defender.attack_roll()
                if attack_roll >= self.attacker.db.attributes['temp_armor_rating']:
                    if 'defend' in atk_action:
                        self.attacker.msg("{bYou easily defend against %s's attack, negating any damage.{n" % self.defender.name)
                        return
                    elif 'attack' in atk_action:
                        attack_roll = self.attacker.attack_roll()
                        if attack_roll >= self.defender.db.attributes['armor_rating']:
                            self.score_hit(who="attacker")
                        else:
                            self.score_miss(who="attacker")
                    elif 'skill' in atk_action:
                        split = atk_action.split(':')
                        #self.attacker.msg("You prepare to use the skill: {g%s{n!" % split[1].title())
                        #self.check_for_combo()
                        manager = self.attacker.db.skill_log
                        character_skills = manager.db.skills
                        if split[1] in character_skills.keys():
                            skill_obj = character_skills[split[1]]
                            skill_obj.on_use(caller=self.attacker)
                    else:
                        pass
                    self.score_hit(who='defender')
                else:
                    self.score_miss(who='defender')
                    if 'defend' in atk_action:
                        self.attacker.msg("{bYou easily defend against %s's attack, negating any damage.{n" % self.defender.name)
                        return
                    elif 'attack' in atk_action:
                        attack_roll = self.attacker.attack_roll()
                        if attack_roll >= self.defender.db.attributes['armor_rating']:
                            self.score_hit(who="attacker")
                        else:
                            self.score_miss(who="attacker")
                    elif 'skill' in atk_action:
                        split = atk_action.split(':')
                        self.attacker.msg("You prepare to use the skill: {g%s{n!" % split[1].title())
                        #self.check_for_combo()
                        manager = self.attacker.db.skill_log
                        character_skills = manager.db.skills
                        if split[1] in character_skills.keys():
                            skill_obj = character_skills[split[1]]
                            skill_obj.on_use(caller=self.attacker)

            else:
                self.attacker.msg("No action selected, probably because I couldnt pop shiz off the deque.")

    def check_for_combo(self):
        prev_action = self.db.prev_atk_action
        adj_action = self.db.adj_action
        
        

    def combat_round(self): 
        """
        This is what controls the combat rounds that get fired off.
        two things that are important:
        --defender = the target of the character/what the character
        chose to attack with the attack command
        --attacker = player character.
        """
        self.attacker_initiative = self.attacker.initiative_roll()
        self.defender_initiative = self.defender.initiative_roll()
        if len(self.attacker_queue) >= len(self.defender_queue):
            self.process_action()
        elif len(self.attacker_queue) < 1:
            self.process_action()
        else:
            self.process_action() 
        #self.attacker.msg("Combat round complete.  Queue up to four of your next actions.")

        """
        if self.attacker_initiative > self.defender_initiative: 
            self.attacker.msg("{rYou begin your assult against: %s (You rolled a %s and they rolled a %s){n" \
                                        % (self.defender.key, self.attacker_initiative, self.defender_initiative))
            attacker_roll = self.attacker.attack_roll()
#            self.attacker.msg("DEBUG: Your attack roll: %s vs %s armor" % (attacker_roll, self.defender.db.attributes['armor_rating']))
            if attacker_roll >= self.defender.db.attributes['armor_rating']: 
                self.score_hit(who="attacker")
            else:
                self.score_miss(who="attacker")
            
            #check if the opponent is dead before they take their turn
            if self.defender.db.corpse is True:
                return
    
            defender_roll = self.defender.attack_roll()
            #self.attacker.msg("DEBUG: Defender attack roll: %s vs %s armor"% (defender_roll, self.attacker.db.attributes['armor_rating']))
            if defender_roll >= int(self.attacker.db.attributes['temp_armor_rating']):
                self.score_hit(who="defender")
            else:
                self.score_miss(who="defender")
        else:
            self.attacker.msg("{r%s gets the jump on you and begins it's assault! (They rolled a %s and you rolled a %s){n" \
                                     % (self.defender.key, self.defender_initiative, self.attacker_initiative))
            defender_roll = self.defender.attack_roll()
            #self.attacker.msg("DEBUG: Defender attack roll: %s vs %s armor" % (defender_roll, self.attacker.db.armor_rating))
            if defender_roll >= int(self.attacker.db.attributes['temp_armor_rating']):
                self.score_hit(who="defender")
            else:
                self.score_miss(who="defender")
            
            if self.attacker.db.in_combat is False: 
                #assume death has occured
                return  

            attacker_roll = self.attacker.attack_roll()
            self.attacker.msg("DEBUG: Your attack roll: %s vs %s armor" % (attacker_roll, self.defender.db.attributes['armor_rating']))
            if attacker_roll >= self.defender.db.attributes['armor_rating']:
                self.score_hit(who="attacker")
            else:
                self.score_miss(who="attacker")
        """
