from ev import Script


class TrashMan(Script):
    """
    This script runs every x interval on the blackhole room cleaning it up and deleting whats there.
    """

    def at_script_creation(self):
        self.persistent = True
        self.interval = 1200
        self.desc = 'Cleans out the blackhole room.'
        
    def at_repeat(self):
        if len(self.obj.contents) > 0:
            for item in self.obj.contents:
                item.delete()
        
        floating_skills = self.obj.search('mob_skills', global_search=True, ignore_errors=True)
        for item in floating_skills:
            if item.db.character is None:
                item.delete()

    def is_valid(self):
        return True
