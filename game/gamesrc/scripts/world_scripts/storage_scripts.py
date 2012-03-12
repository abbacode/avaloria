from game.gamesrc.scripts.basescript import Script


class OpenState(Script):
    """
    gets attached to an open chest object
    """

    def at_script_creation(self):
        self.persistent = False
        self.interval = 15
        self.start_selay = True
        self.desc = "keeps the lid open for ya"
        
    def at_repeat(self):
        self.obj.close_storage()
    
    def is_valid(self):
        return self.obj.db.is_open
