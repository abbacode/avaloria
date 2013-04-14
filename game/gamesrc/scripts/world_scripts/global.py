from ev import Script
from src.utils import search

class MobRunner(Script):
    """
    Controls when the update functions for mobs are called.  Holds
    a list of dbref's for subscribing objects (Mobs)
    """

    def at_script_creation(self):
        self.key = 'mob_runner'
        self.interval =  30
        self.persistent = True
        self.desc = 'controls the subscribing mobs'
        self.db.mobs = [] 
         
    def at_start(self):
        self.ndb.mobs = [ search.objects(dbref) for dbref in self.db.mobs ]
        
    def at_repeat(self):
        self.ndb.mobs = search.objects('mob_runner')
        print "MobRunner ==> update()"
        [mob.update() for mob in self.ndb.mobs if mob.db.should_update and mob is not None]
        print "MobRunner ==> kos_tick()"
        [mob.kos_tick() for mob in self.ndb.mobs if mob.db.is_kos and mob.db.should_update and mob is not None]

    def at_stop(self):
        self.db.mobs = [mob.dbref for mob in self.ndb.mobs]
    

class IrregularRunner(Script):
    """
    fires off irregular events, like skill usage in combat
    """

    def at_script_creation(self):
        self.key = 'irregular runner'
        self.interval = 20 
        self.persistent = True
        self.desc = 'controls the irregular events of subscribers'
        self.db.subscribers = []

    def at_start(self):
        self.ndb.mobs = [ search.objects(dbref) for dbref in self.db.subscribers]

    def at_repeat(self):
        self.ndb.mobs = search.objects('irregular_runner') 
        [mob.irregular_action() for mob in self.ndb.mobs if mob.db.should_update]

class NpcRunner(Script):
    """
    Manages NPC's
    subscribers = npc objects (global scope) with the 'npc_runner' alias

    This script cycles through its subscribers calling the .update() function
    on them.
    """

    def at_script_creation(self):
        self.key = 'npc_runner'
        self.interval = 60
        self.persistent = True
        self.desc = 'controls the update of npc objects subscribed'
        self.db.subscribers = []

    def at_start(self):
        self.ndb.subscribers = [ search.objects(dbref) for dbref in self.db.subscribers ]
       
    def at_repeat(self):
        self.ndb.subscribers = search.objects('npc_runner')
        [npc.update() for npc in self.ndb.subscribers]

class ZoneRunner(Script):
    """
    Updates the zone manager objects, firing off mob respawn and the like.

    This script does three specific tasks:
        - Reanimates mobs that are flagged to do so.
        - Updates the subscribed zones (this means replenishing mobs and quest items)
        - Deletes corpses that have not been looted.

    subscribers = zone objects subscribed to this sentinel
    reanimators = npc objects with the alias of 'reanimator'
    corpses = corpse objects that have been left laying around ('corpse' alias).
    """
    def at_script_creation(self):
        self.key = "zone_runner"
        self.interval = 300
        self.persistent = True
        self.desc = 'controls the subscribing zones.'
        self.db.subscribers = []
        self.db.corpses = []
        self.db.reanimators = []

    def at_start(self):
        self.ndb.subscribers = [ search.objects(dbref) for dbref in self.db.subscribers]
        self.ndb.corpses = [search.objects(dbref) for dbref in self.db.corpses ]
        self.ndb.reanimators = [search.objects(dbref) for dbref in self.db.reanimators]

    def at_repeat(self):
        print "ZoneRunner ==> reanimate()"
        self.ndb.reanimators = search.objects('reanimator')
        [reanimator.reanimate() for reanimator in self.ndb.reanimators if reanimator.db.corpse]
        print "ZoneRunner ==> update()"
        self.ndb.subscribers = search.objects('zone_runner')
        [zone.update() for zone in self.ndb.subscribers if not zone.db.mobs_spawned ]
        print "ZoneRunner ==> corpse.delete()"
        self.ndb.corpses = search.objects('corpse')
        [corpse.delete() for corpse in self.ndb.corpses if not corpse.db.reanimate ]
        
class LairRunner(Script):
    """
    Manages player lair's
    """
    def at_script_creation(self):
        self.key = 'lair_runner'
        self.interval = 60 * 60
        self.persistent = True
        self.desc = 'controls the subscribing lairs'
        self.db.subscribers = []

    def at_start(self):
        self.ndb.subscribers = [search.objects(dbref) for dbref in self.db.subscribers]
        
    def at_repeat(self):
        self.ndb.subscribers = search.objects('lair_runner')
        [lair.update() for lair in self.ndb.subscribers]
        
