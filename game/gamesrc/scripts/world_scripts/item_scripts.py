from ev import Script


class StateLightSourceOn(Script):
    """
    Script used to keep track of a light source item being on or off.
    """
    def at_script_creation(self):
        self.key = "torch_burn"
        self.desc = "Keept tabs on light sources"
        self.interval = self.obj.db.burntime
        self.start_delay = True
        self.repeats = 1
        
    def at_start(self):
        self.obj.location.location.msg_contents("{C%s lights a torch.{n" % self.obj.location.name)

    def at_repeat(self):
        self.obj.reset()

    def is_valid(self):
        return self.obj.is_active
        
