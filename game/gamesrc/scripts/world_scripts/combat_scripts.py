import random
from src.utils import create
from ev import Script


class InCombatState(Script):
    
    def at_script_creation(self):
        self.key = 'battle_arbiter'
        self.interval = 3
        self.persistent = False
        self.desc = "Combat Arbitration Script"
    
    def at_start(self):
        self.obj.db.in_combat = True
        self.db.unbalanced_message_sent = False
        cm = create.create_object("game.gamesrc.objects.world.combat.CombatManager", key="%s_combat_manager" % self.obj.name)
        if self.obj.db.cmd_id is not None:
            cm = self.obj.db.cm_id
            cm.delete()

        self.obj.db.cm_id = cm
        cm.db.rounds = 0
        cm.attacker = self.obj
        cm.attacker_queue = self.obj.db.combat_queue
        cm.defender = self.obj.db.target
        cm.defender_queue = cm.defender.db.combat_queue
        cm.generate_texts()

    def at_repeat(self):
        cm = self.obj.db.cm_id
        cm.attacker_queue = self.obj.db.combat_queue
        cm.defender_queue = cm.defender.db.combat_queue
        cm.db.rounds += 1
        character_balance = cm.attacker.db.attributes['temp_balance']
        self.obj.msg("{CNew Round.{n Rounds Fought: {G%s{n" % cm.db.rounds)

        if character_balance == 2:
            if self.db.unbalanced_message_sent is not True:
                self.obj.msg("{CYou feel slightly off balance.{n")
                self.db.unbalanced_message_sent = True
            self.obj.unbalance(phase=1)
        elif character_balance == 1:
            if self.db.unbalanced_message_sent is not False:
                self.obj.msg("{RYou are exhausted, any use of combat skills will result in a further,\n and further decrease in: attack rating, dexterity, and strength.{n")
                self.db.unbalanced_message_sent = False
            self.obj.unbalance(phase=2)
        elif character_balance ==  0:
            if self.db.unbalanced_message_sent is not True:
                self.obj.msg("{rYou are so exhausted you are on the brink of passing out. {n")
                self.db.unbalanced_message_sent = True
            self.obj.unbalance(phase=3)

        if self.obj.db.attributes['temp_health'] > 0 and cm.defender.db.attributes['temp_health'] > 0:
            cm.combat_round()
        elif self.obj.db.target.db.attributes['temp_health'] <= 0:
            cm.check_quest_flags()
            self.obj.db.in_combat = False
            cm.defender = self.obj.db.target
            self.obj.msg("{bYou have defeated your foe!{n")
            self.obj.award_exp(cm.defender.db.attributes['exp_award'])
            self.obj.db.target.death()
        elif self.obj.db.attributes['temp_health'] <= 0:
            self.obj.msg("{rYou have been killed by %s!" % self.obj.db.target.name)
            self.obj.location.msg_contents("{r%s has be slain by %s!{n" % (self.obj.name, cm.defender.name), exclude=[cm.db.attacker])
            self.obj.db.target.db.in_combat = False
            self.obj.db.target.db.target = None
            print "got to death call"
            self.obj.db.in_combat = False
            self.obj.death()
    
    def at_stop(self):
        cm = self.obj.db.cm_id
        if cm is not None:
            cm.delete()

    def is_valid(self):
        return self.obj.db.in_combat

class UnbalancedState(Script):
    """
    This script monitors character balance and restores it when necessary.
    """
    
    def at_script_creation(self):
        self.key = 'unbalanced_state'
        self.interval = 20
        self.persistent = True
        self.start_delay = True

    def at_start(self):
        self.db.am_i_needed = True
       
    def at_repeat(self):
        character_attributes = self.obj.db.attributes
        
        if character_attributes['temp_balance'] < character_attributes['balance']:
            character_attributes['temp_balance'] = character_attributes['temp_balance'] + 1
            self.obj.db.attributes = character_attributes
            self.obj.msg("{bYou regain some of your balance.{n")
        elif character_attributes['temp_balance'] == character_attributes['balance']:
            self.obj.db.attributes = character_attributes
            self.obj.balance()
            self.obj.msg("{bYou feel fully balanced.{n")
            self.db.am_i_needed = False
        
    
    def is_valid(self):
        return self.db.am_i_needed
            
            
    def at_stop(self):
        self.obj.db.unbalanced = False
