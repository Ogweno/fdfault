from __future__ import division, print_function

class interface(object):
    def __init__(self, index, direction, bm, bp):
        "Initializes interface given an index, direction, and block coordinates"
        assert index >= 0, "interface index must be nonnegative"
        assert (direction == "x" or direction == "y" or direction == "z"), "Direction must be x, y, or z"
        assert len(bm) == 3, "must provide 3 integers for block indices"
        assert len(bp) == 3, "must provide 3 integers for block indices"
        for i in range(3):
            assert bm[i] >= 0, " block indices must be nonegative"
            assert bp[i] >= 0, "block indices must be nonnegative"

        if direction == "x":
            assert int(bp[0])-int(bm[0]) == 1, "blocks must be neighboring to be coupled via an interface"
            assert int(bp[1]) == int(bm[1]), "blocks must be neighboring to be coupled via an interface"
            assert int(bp[2]) == int(bm[2]), "blocks must be neighboring to be coupled via an interface"
        elif direction == "y":
            assert int(bp[1])-int(bm[1]) == 1, "blocks must be neighboring to be coupled via an interface"
            assert int(bp[0]) == int(bm[0]), "blocks must be neighboring to be coupled via an interface"
            assert int(bp[2]) == int(bm[2]), "blocks must be neighboring to be coupled via an interface"
        else:
            assert int(bp[2])-int(bm[2]) == 1, "blocks must be neighboring to be coupled via an interface"
            assert int(bp[0]) == int(bm[0]), "blocks must be neighboring to be coupled via an interface"
            assert int(bp[1]) == int(bm[1]), "blocks must be neighboring to be coupled via an interface"

        self.iftype = "locked"
        self.index = int(index)
        self.bm = (int(bm[0]), int(bm[1]), int(bm[2]))
        self.bp = (int(bp[0]), int(bp[1]), int(bp[2]))
        self.direction = direction
        self.surf = None

    def get_direction(self):
        "Returns interface orientation"
        return self.direction

    def get_index(self):
        "Returns index"
        return self.index

    def set_index(self,index):
        "Sets index"
        assert index >= 0, "interface index must be nonnegative"
        self.index = index

    def get_type(self):
        "Returns string of interface type"
        return self.iftype

    def get_bm(self):
        "Returns block on negative side"
        return self.bm

    def get_bp(self):
        "Returns block on positive side"
        return self.bp

    def get_nloads(self):
        "Returns number of load perturbations"
        raise NotImplementedError, "Interfaces do not support load perturbations"

    def add_load(self, newload):
        "Adds a load to list of load perturbations"
        raise NotImplementedError, "Interfaces do not support load perturbations"

    def get_dc(self):
        "Returns slip weakening distance"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def set_dc(self, dc):
        "Sets slip weakening distance"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def get_mus(self):
        "Returns static friction coefficient"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def set_mus(self, mus):
        "Sets static friction coefficient"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def get_mud(self):
        "Returns dynamic friction coefficient"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def set_mud(self, mud):
        "Sets dynamic friction coefficient"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def get_params(self):
        "Returns all friction parameters as a tuple"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def set_params(self, dc, mus, mud):
        "Set all friction parameters"
        raise NotImplementedError, "Interfaces do not support friction parameters"

    def write_input(self,f):
        "Writes interface details to input file"
        f.write("[fdfault.interface"+str(self.index)+"]\n")
        f.write(self.direction+"\n")
        f.write(str(self.bm[0])+" "+str(self.bm[1])+" "+str(self.bm[2])+"\n")
        f.write(str(self.bp[0])+" "+str(self.bp[1])+" "+str(self.bp[2])+"\n")
        if self.surf is None:
            f.write("none\n")
        else:
            raise NotImplementedError, "Surface files not implemented"
        f.write("\n")
    
    def __str__(self):
        return 'Interface '+str(self.index)+":\ndirection = "+self.direction+"\nbm = "+str(self.bm)+"\nbp = "+str(self.bp)

class friction(interface):
    def __init__(self, index, direction, bm, bp):
        "Initializes frictional interface, also calls __init__ method of interface"
        interface.__init__(self, index, direction, bm, bp)
        self.iftype = "frictionless"
        self.nloads = 0
        self.loads = []

    def get_nloads(self):
        "Returns number of load perturbations"
        return self.nloads

    def add_load(self,newload):
        "Adds a load to list of load perturbations"
        assert type(newload) is load, "Cannot add types other than loads to load list"
        self.loads.append(newload)

    def write_input(self,f):
        "Writes Interface to input file"
        interface.write_input(self, f)
        f.write("[fdfault.friction]\n")
        f.write(str(self.nloads))

        for l in self.loads:
            l.write_input(f)

        f.write("\n")
        
    def __str__(self):
        "Returns string representation of interface"
        loadstring = ""
        for load in self.loads:
            loadstring += "\n"+str(load)
        return ('Frictional interface '+str(self.index)+":\ndirection = "+self.direction+
                "\nbm = "+str(self.bm)+"\nbp = "+str(self.bp)+"\nnloads = "+str(self.nloads)+"\nLoads:"+loadstring)

class slipweak(friction):
    "Class describing slip weakening friction interface"
    def __init__(self, index, direction, bm, bp):
        friction.__init__(self, index, direction, bm, bp)
        self.iftype = "slipweak"
        self.dc = 0.
        self.mus = 0.
        self.mud = 0.

    def get_dc(self):
        "Returns slip weakening distance"
        return self.dc

    def set_dc(self, dc):
        "Sets slip weakening distance"
        assert dc >= 0., "slip weakening distance cannot be negative"
        self.dc = float(dc)

    def get_mus(self):
        "Returns static friction coefficient"
        return self.mus

    def set_mus(self, mus):
        "Sets static friction coefficient"
        assert mus >= 0., "static friction coefficient cannot be negative"
        self.mus = float(mus)

    def get_mud(self):
        "Returns dynamic friction coefficient"
        return self.mud

    def set_mud(self, mud):
        "Sets dynamic friction coefficient"
        assert mud >= 0., "dynamic friction coefficient cannot be negative"
        self.mud = float(mud)

    def get_params(self):
        "Returns all friction parameters as a tuple"
        return (self.dc, self.mus, self.mud)

    def set_params(self, dc, mus, mud):
        "Set all friction parameters"
        self.set_dc(dc)
        self.set_mus(mus)
        self.set_mud(mud)

    def write_input(self, f):
        "Write parameters to input file"
        friction.write_input(self,f)

        f.write("[fdfault.slipweak]\n")
        f.write(str(dc)+"\n")
        f.write(str(mus)+"\n")
        f.write(str(mud)+"\n")

        f.write("\n")

    def __str__(self):
        "Returns string representation of slipweakening friction law"
        loadstring = ""
        for load in self.loads:
            loadstring += "\n"+str(load)
        return ('Slip weakening interface '+str(self.index)+":\ndirection = "+self.direction+
                "\nbm = "+str(self.bm)+"\nbp = "+str(self.bp)+"\ndc = "+str(self.dc)+", mus = "
                +str(self.mus)+", mud = "+str(self.mud)+"\nnloads = "+str(self.nloads)+"\nLoads:"+loadstring)

class load(object):
    "Class representing load perturbations to fricitonal interfaces"
    def __init__(self, loadtype = 'constant', t0 = 0., x0 = 0., dx = 0., y0 = 0., dy = 0., sn = 0., s2 = 0., s3 =0.):
        "Initialize interface load perturbation"
        assert (loadtype == "gaussian" or loadtype == "constant" or loadtype == "ellipse"
                or loadtype == "boxcar"), "Load must be constant, gaussian, ellipse, or boxcar"
        assert t0 >= 0., "t0 must be nonnegative"
        assert dx >= 0., "dx must be nonnegative"
        assert dy >= 0., "dy must be nonnegative"
        
        self.loadtype = loadtype
        self.t0 = float(t0)
        self.x0 = float(x0)
        self.y0 = float(y0)
        self.dx = float(dx)
        self.dy = float(dy)
        self.sn = float(sn)
        self.s2 = float(s2)
        self.s3 = float(s3)

    def write_input(self, f):
        "Writes loads to input file"
        f.write(self.loadtype+" "+str(self.t0)+" "+str(self.x0)+" "+str(self.dx)+" "+str(self.y0)+
                " "+str(self.dy)+" "+str(self.sn)+" "+str(self.s2)+" "+str(self.s3)+"\n")

    def __str__(self):
        "Returns a string representation"
        return ("type = "+self.loadtype+", t0 = "+str(self.t0)+", x0 = "+str(self.x0)+", dx = "+str(self.dx)+
                ", y0 = "+str(self.y0)+", dy = "+str(self.dy)+", sn = "+str(self.sn)+", s2 = "+str(self.s2)+", s3 = "+str(self.s3))
    