import random, time
from collections import deque
from ev import Object

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
        self.opponent_missed_attacks_text = ["%s misses you with their wild attack." % self.defender.key,
                                                "%s clumsily tries to attack you, but misses horribly." % self.defender.key,
                                                "%s comes at you, but is deflected by your armor." % self.defender.key,
                                                "%s swings at you mightily, but misses." % self.defender.key]
    def check_for_dodge(self, who):
        char_obj = who
        dodge_roll = random.random()
        if dodge_roll <= char_obj.db.percentages['dodge']:
            return True
        else:
            return False

    def score_hit(self, who, crit=False):
        character_weapon = self.attacker.db.equipment['weapon']
        skill_manager = self.attacker.db.skill_log
        print "scoring a hit.."
        if 'attacker' in who:
            print "Checking crit."
            if crit:
                damage_amount = self.attacker.get_damage()
                damage_amount = character_weapon.critical(damage_amount)
            else:
                damage_amount = self.attacker.get_damage()

            print "Checking for weapon.."
            if character_weapon is not None:
                if character_weapon.db.skill_used not in skill_manager.db.skills.keys():
                    rn = random.random()
                    if rn > self.attacker.db.percentages[character_weapon.db.skill_used]:
                        damage_amount = self.attacker.do_glancing_blow()
                
            if character_weapon is None:
                self.punching_texts = ["You pummel %s with a flurry of punches for {R%s{n damage!" % (self.defender.key, damage_amount),
                                            "You connect with a quick jab for {R%s{n damage!" % damage_amount,
                                            "You uppercut %s for {R%s{n damage!" % (self.defender.key, damage_amount),
                                            "As you throw a punch, you feel it connect for {R%s{n damage!" % damage_amount ]
                msg_text = random.choice(self.punching_texts)
            else:
                equipment = self.attacker.db.equipment
                weapon = equipment['weapon']
                self.character_hit_text = ["You swing your %s at full force, hitting for {R%s{n damage!" % (weapon.name, damage_amount),
                                                "You deal {R%s{n damage to %s!" % (damage_amount, self.defender.key),
                                                "You bring your %s down on %s's head for {R%s{n damage!" % (weapon.name, self.defender.key, damage_amount),
                                                "Striking with vengence you do {R%s{n damage!" % damage_amount]
                msg_text = random.choice(self.character_hit_text)
                if crit:
                    msg_text += " {RCritical hit!!{n"
            self.defender.take_damage(damage=damage_amount)
            self.attacker.msg(msg_text)
            
           # self.attacker.msg(You deal {r%s{n damage to %s." % (damage_amount, self.defender.key ))
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
            print "Done with hit."
            return
        else:
            damage_amount = self.defender.get_damage()
            self.attacker.take_damage(damage=damage_amount)
            self.attacker.msg("You take {r%s{n points of damage." % damage_amount)
            self.attacker.msg("{rHP: (%s/%s){n {bMP: (%s/%s){n" % (self.attacker.db.attributes['temp_health'], self.attacker.db.attributes['health'], 
                                        self.attacker.db.attributes['temp_mana'], self.attacker.db.attributes['mana']))
            print "done with hit"
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
        print "Processing combat action.."
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
        print 'Proper variables assigned..'
        
        #self.attacker.msg("{yYour Attack Queue: {g%s{n" % self.attacker_queue)
        self.attacker_initiative = self.attacker.initiative_roll()
        self.defender_initiative = self.defender.initiative_roll()
        if self.db.attacker.db.equipment['weapon'] is not None:
            weapon = self.attacker.db.equipment['weapon']
            crit_roll = weapon.db.crit_range.split('-')
        else:
            crit_roll = None
        
        crit = False
        if self.attacker_initiative > self.defender_initiative or self.defender.db.stunned:
            print "Character attacking first..."
            if 'attack' in atk_action: 
                attack_roll = self.attacker.attack_roll()
                if crit_roll:
                    for i in range(int(crit_roll[0]), int(crit_roll[1]) + 1):
                        if attack_roll >= i:
                            crit = True
                            break

                if attack_roll >= self.defender.db.attributes['armor_rating'] or self.defender.db.stunned:
                    if not self.defender.db.stunned:
                        dodge_result = self.check_for_dodge(self.db.defender)
                    else:
                        dodge_result = None
                    self.attacker.armor_unbalance_check()
                    if dodge_result:
                        self.attacker.msg("{c%s dodged your attack!{n" % self.defender.name)
                    if 'defend' in def_action and not self.defender.db.stunned:
                        self.attacker.msg("%s is in a defensive position, negating your attack." % self.defender.name)
                        return
                    elif 'attack' in def_action and not self.defender.db.stunned:
                        print "checking for mob skill proc..."
                        if self.check_for_mob_skill_proc():
                            return
                        defender_attack_roll = self.defender.attack_roll()
                        if defender_attack_roll >= self.attacker.db.attributes['temp_armor_rating']:
                            self.score_hit(who='defender')
                        else:
                            self.score_miss(who='defender')                 
                    else:
                        pass
                        #do nothing    

                    if dodge_result:
                        return

                    self.score_hit(who="attacker", crit=crit)
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
               
                if 'attack' in def_action:
                    def_atk_roll = self.defender.attack_roll()
                    if def_atk_roll >= self.attacker.db.attributes['temp_armor_rating']:
                        self.score_hit(who="defender")
                    else:
                        self.score_miss(who="defender")
 
            else:
                pass
        else:
            print "mob going first..."
            if 'attack' in def_action:
                print "checking for mob skill proc..."
                if self.check_for_mob_skill_proc():
                    return
                attack_roll = self.defender.attack_roll()
                if attack_roll >= self.attacker.db.attributes['temp_armor_rating']:
                    dodge_result = self.check_for_dodge(self.db.attacker)
                    if dodge_result:
                        self.attacker.msg("{CYou swiftly dodge %s's blow.{n" % self.defender.name)
                        
                    if 'defend' in atk_action:
                        self.attacker.msg("{bYou easily defend against %s's attack, negating any damage.{n" % self.defender.name)
                        return
                    elif 'attack' in atk_action:
                        self.attacker.armor_unbalance_check()
                        if crit_roll:
                            for i in range(int(crit_roll[0]), int(crit_roll[1]) + 1):
                                if attack_roll >= i:
                                    crit = True
                                    break
                        attack_roll = self.attacker.attack_roll()
                        if attack_roll >= self.defender.db.attributes['armor_rating']:
                            self.score_hit(who="attacker")
                        else:
                            self.score_miss(who="attacker")
                    elif 'skill' in atk_action:
                        split = atk_action.split(':')
                        #self.attacker.msg("You prepare to use the skill: {C%s{n!" % split[1].title())
                        manager = self.attacker.db.skill_log
                        character_skills = manager.db.skills
                        if split[1] in character_skills.keys():
                            skill_obj = character_skills[split[1]]
                            skill_obj.on_use(caller=self.attacker)
                    else:
                        pass

                    if dodge_result:
                        return
    
                    if self.defender.db.stunned:
                        return
                    self.score_hit(who='defender')
                else:
                    self.score_miss(who='defender')
                    if 'defend' in atk_action:
                        self.attacker.msg("{bYou easily defend against %s's attack, negating any damage.{n" % self.defender.name)
                        return
                    elif 'attack' in atk_action:
                        if crit_roll:
                            for i in crit_roll:
                                if attack_roll >= i:
                                    print "Scored a crit"
                                    crit = True

                        attack_roll = self.attacker.attack_roll()
                        if attack_roll >= self.defender.db.attributes['armor_rating']:
                            self.score_hit(who="attacker")
                        else:
                            self.score_miss(who="attacker")
                    elif 'skill' in atk_action:
                        split = atk_action.split(':')
                        #self.attacker.msg("You prepare to use the skill: {C%s{n!" % split[1].title())
                        manager = self.attacker.db.skill_log
                        character_skills = manager.db.skills
                        if split[1] in character_skills.keys():
                            skill_obj = character_skills[split[1]]
                            skill_obj.on_use(caller=self.attacker)

            else:
                self.attacker.msg("No action selected, probably because I couldnt pop shiz off the deque.")

        

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


    def check_for_mob_skill_proc(self):
        chance = 0.20
        rn = random.random()
        print "chance => %s.....rn => %s" % (chance, rn)
        if rn < chance:
            if 'brute' in self.defender.db.combat_type:
                print "picking a skill"
                skills = ['bash', 'crush']
                skill = random.choice(skills)
                print "excecuting: %s" % skill
                self.defender.execute_cmd('%s' % skill.strip())
            return True
        else:
            return False
            
                
