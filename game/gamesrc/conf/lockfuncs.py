"""

This is an example module for holding custom lock funcs, used in
in-game locks.  The modules available to use as lockfuncs are defined
in the tuple settings.LOCK_FUNC_MODULES.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See
http://code.google.com/p/evennia/wiki/Locks

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled (excess ones calling magic (*args,
**kwargs) to avoid errors). The lock function should handle all
eventual tracebacks by logging the error and returning False.

See many more examples of lock functions in src.locks.lockfuncs. 

"""
def onquest(accessing_obj, accessed_obj, *args, **kwargs):
    character = accessing_obj
    quest = args[0]
    ql = character.db.quest_log
    if character.on_quest(quest):
        return True
    else:
        return False

def completed_quest(accessing_obj, accessed_obj, *args, **kwargs):
    character = accessing_obj
    quest = args[0]
    return character.on_quest(quest, completed=True)

def holds(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Usage: 
      holds()          # checks if accessed_obj or accessed_obj.obj is held by accessing_obj
      holds(key/dbref) # checks if accessing_obj holds an object with given key/dbref

    This is passed if accessed_obj is carried by accessing_obj (that is,
    accessed_obj.location == accessing_obj), or if accessing_obj itself holds an
    object matching the given key.
    """
    print "checking holds..."
    try:
        # commands and scripts don't have contents, so we are usually looking
        # for the contents of their .obj property instead (i.e. the object the
        # command/script is attached to). 
        contents = accessing_obj.contents
    except AttributeError:
        try:
            contents = accessing_obj.obj.contents
        except AttributeError:
            return False

    def check_holds(objid):
        # helper function. Compares both dbrefs and keys/aliases.
        objid = str(objid)
        dbref = utils.dbref(objid)
        print "checking dbrefs for %s: %s" % (objid, dbref)
        if dbref and any((True for obj in contents if obj.id == dbref)):
            return True

        objid = objid.lower()
        for obj in contents:
            print "objid: %s\t obj.key: %s" % (objid, obj.key.lower())
            for thing in obj.contents:
                print thing
                if thing.key.lower() == objid or objid in [al.lower() for al in thing.aliases]:
                    return True
        return any((True for obj in contents
                    if obj.key.lower() == objid or objid in [al.lower() for al in obj.aliases]))

    if args and args[0]:
        return check_holds(args[0])
    else:
        try:
            if check_holds(accessed_obj.id):
                print "holds: accessed_obj.id - True"
                return True
        except Exception:
            pass
        print "holds: accessed_obj.obj.id -", hasattr(accessed_obj, "obj") and check_holds(accessed_obj.obj.id)
        return hasattr(accessed_obj, "obj") and check_holds(accessed_obj.obj.id)

def myfalse(accessing_obj, accessed_obj, *args, **kwargs):
    """
    called in lockstring with myfalse().  
    A simple logger that always returns false. Prints to stdout
    for simplicity, should use utils.logger for real operation.
    """
    print "%s tried to access %s. Access denied." % (accessing_obj, accessed_obj)
    return False 
