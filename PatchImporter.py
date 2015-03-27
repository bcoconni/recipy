import sys
import imp

import functools
from datetime import timedelta 

class PatchImporter(object):
    modulename = 'pandas'

    def find_module(self, fullname, path=None):
        """Module finding method. It tells Python to use our hook
        only for the pytz package.
        """
        if fullname == self.modulename:
            self.path = path
            return self
        return None
    
    def load_module(self, name):
        """Module loading method. It imports pytz normally
        and then enhances it with our generic timezones.
        """
        if name != self.modulename:
            raise ImportError("%s can only be used to import pandas!",
                              self.__class__.__name__)
        if name in sys.modules:
            return sys.modules[name]    # already imported
        
        file_obj, pathname, desc = imp.find_module(name, self.path)
        try:
            mod = imp.load_module(name, file_obj, pathname, desc)
        finally:
            if file_obj:
                file_obj.close()
        
        print "Patching %s" % mod.__name__
        mod = self.patch(mod)
        sys.modules[name] = mod
        return mod

    
    def patch(self, mod):
        return mod

    def patch_function(self, mod, function, wrapper):
        old_f_name = '_%s' % function.replace(".", "_")
        setattr(mod, old_f_name, recursive_getattr(mod, function))

        recursive_setattr(mod, function, wrapper(getattr(mod, old_f_name)))

#sys.meta_path = [PatchImporter()]