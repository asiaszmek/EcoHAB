#!/usr/bin/env python
# encoding: utf-8
from __future__ import division, absolute_import, print_function

import os
import glob
import sys

from pyEcoHAB import data_path

if sys.version_info < (3, 0):
    from ConfigParser import RawConfigParser, NoSectionError
else:
    from configparser import RawConfigParser, NoSectionError


class SetupConfig(RawConfigParser):
    ALL_ANTENNAS = ["1", "2", "3", "4", "5", "6", "7", "8"]
    def __init__(self, path=None, fname=None):    
        RawConfigParser.__init__(self)
        if path is None:
            self.path = data_path
            self.fname = "standard_setup.txt"
        else:
            self.path = path
            if fname is not None:
                self.fname = fname
            else:
                if os.path.isfile(os.path.join(self.path, 'setup.txt')):
                    self.fname = 'setup.txt'
                else:
                    fnames = glob.glob(os.path.join(path, "setup*txt"))
                    if len(fnames):
                        self.fname = os.path.basename(fnames[0])
                        self.path = path
                    else:
                       print("No setup config found in %s" % path)
                       self.path = data_path
                       self.fname = "standard_setup.txt"

        full_path = os.path.join(self.path, self.fname)
        self.read(full_path)

        self.cages = self.get_cages()
        self.tunnels = self.get_tunnels()
        self.cages_dict = self.get_cages_dict()
        self.tunnels_dict = self.get_tunnels_dict()
        self.same_tunnel = self.get_same_tunnel()
        self.same_address = self.get_same_address()
        self.opposite_tunnel = self.get_opposite_tunnel_dict()
        self.address = self.get_cage_address_dict()
        self.address_non_adjacent = self.get_address_non_adjacent_dict()
        self.address_surrounding = self.get_surrounding_dict()
        self.directions = self.get_directions_dict()
        self.mismatched_pairs = self.get_mismatched_pairs()

    def get_cages(self):
        return sorted(filter(lambda x: x.startswith("cage"),
                      self.sections()))

    def get_tunnels(self):
        return sorted(filter(lambda x: x.startswith("tunnel"),
                      self.sections()))

    def get_cages_dict(self):
        cage_dict = {}
        cages = self.get_cages()
        for sec in cages:
            cage_dict[sec] = []
            for antenna_type, val in self.items(sec):
                if antenna_type.startswith("entrance"):
                    cage_dict[sec].append(int(val))
                elif antenna_type.startswith("internal"):
                    continue
                else:
                    print("Unknown antenna type %s" % antenna_type)
            if not len(cage_dict[sec]):
                print("Did not register any antennas associated with %s", sec)
        if not len(list(cage_dict.keys())):
            print("Did not registered any cages in this setup")
        return cage_dict

    def get_tunnels_dict(self):
        tunnel_dict = {}
        tunnels = self.get_tunnels()
        for sec in tunnels:
            tunnel_dict[sec] = []
            for antenna_type, val in self.items(sec):
                if antenna_type.startswith("entrance"):
                    tunnel_dict[sec].append(int(val))
                else:
                    print("Unknown antenna type %s" % antenna_type)
            if not len(tunnel_dict[sec]):
                print("Did not register any antennas associated with %s", sec)
        if not len(list(tunnel_dict.keys())):
            print("Did not registered any tunnels in this setup")
        return tunnel_dict

    @property
    def internal_antennas(self):
        out = []
        for sec in self.sections():
            all_items = self.items(sec)
            out += [sec for item in all_items if item[0].startswith("int")]
        return out

    def get_same_tunnel(self):
        tunnel_dict = self.get_tunnels_dict()
        out = {}
        for tunnel, value in tunnel_dict.items():
            for antenna in value:
                out[int(antenna)] = [int(val) for val in value]
        return out

    def get_same_address(self):
        cage_dict = self.get_cages_dict()
        out = {}
        for cage, value in cage_dict.items():
            for antenna in value:
                out[int(antenna)] = value
        return out

    @property
    def entrance_antennas(self):
        out = []
        for sec in self.sections():
            for key, value in self.items(sec):
                if key.startswith("entrance") and int(value) not in out:
                    out.append(int(value))
        return out

    def other_tunnel_antenna(self, new_antenna):
        antenna = int(new_antenna)
        tunnel_antennas = self.same_tunnel[antenna][:]
        idx = tunnel_antennas.index(antenna)
        tunnel_antennas.pop(idx)
        return tunnel_antennas

    def other_cage_antenna(self, new_antenna):
        antenna = int(new_antenna)
        cage_antennas = self.same_address[antenna][:]
        idx = cage_antennas.index(antenna)
        cage_antennas.pop(idx)

        return cage_antennas

    def next_tunnel_antennas(self, antenna):
        out = []
        same_pipe = self.same_tunnel[int(antenna)]
        for ant in same_pipe:
            same_cage_a = self.other_cage_antenna(int(ant))
            for a_2 in same_cage_a:
                other_pipe = self.same_tunnel[int(a_2)]
                if other_pipe != same_pipe:
                    out.extend(other_pipe)
        return sorted(out)

    def get_opposite_tunnel_dict(self):
        # distance equal two
        all_antennas = self.entrance_antennas
        same_cages = self.same_address
        same_pipe = self.same_tunnel
        out = {}
        for a_1 in all_antennas:
            same_cage_antennas = self.other_cage_antenna(int(a_1))

            for a_2 in same_cage_antennas:
                pipe_next = self.other_tunnel_antenna(int(a_2))

                for a_3 in pipe_next:
                    cage_plus_2 = self.other_cage_antenna(int(a_3))

                    for a_4 in cage_plus_2:
                        tunnel_antennas = same_pipe[int(a_4)]
                        next_tunnel_antennas = self.next_tunnel_antennas(int(a_4))
                        if int(a_1) not in tunnel_antennas and int(a_1) not in next_tunnel_antennas:
                            if int(a_1) not in out:
                                out[int(a_1)] = []
                            for ant in tunnel_antennas:
                                if int(ant) not in out[int(a_1)]:
                                    out[int(a_1)].append(int(ant))

        return out

    def get_cage_address_dict(self):
        out = {}
        for sec in self.cages:
            for antenna_type, antenna in self.items(sec):
                if antenna_type.startswith("entrance"):
                    if int(antenna) in out:
                        raise Exception("%s was specified as %s twice"%(antenna_type,
                                                                        antenna))
                    else:
                        out[int(antenna)] = sec
        return out

    def get_address_non_adjacent_dict(self):
        all_antennas = self.entrance_antennas
        out = {}
        cage_dict = self.get_cage_address_dict()
        for antenna in all_antennas:
            pipe_next = self.other_tunnel_antenna(antenna)
            try:
                cage_adjacent = cage_dict[pipe_next[0]]
                out[int(antenna)] = cage_adjacent
            except:
                pass
        return out

    def get_surrounding_dict(self):
        all_antennas = self.entrance_antennas
        out = {}
        cage_dict = self.get_cage_address_dict()

        for antenna in all_antennas:
            pipe_next = self.other_tunnel_antenna(antenna)
            try:
                cage_adjacent_antennas = self.other_cage_antenna(pipe_next[0])
            except:
                continue
            for caa in cage_adjacent_antennas:
                key = (min(int(antenna), int(caa)), max(int(antenna), int(caa)))
                if key not in out:
                    out[key] = cage_dict[caa]
        return out

    def get_directions_dict(self):
        out = []
        for tunnel in self.tunnels:
            vals = [item[1] for item in self.items(tunnel) if item[0].startswith("entra")]
            if len(vals) > 2:
                raise Exception("There are more than 2 antennas at the entrances to %s" % tunnel)
            out += [vals[0]+vals[1], vals[1]+vals[0]]
        return sorted(out)

    def find_unused_antennas(self):
        out_l = []
        for sec in self.sections():
            ants = [item[1] for item in self.items(sec)]
            out_l.extend(ants)
        return sorted(set(self.ALL_ANTENNAS) - set(out_l))

    def get_mismatched_pairs(self):
        pairs = []
        for i in range(1, 9):
            for j in range(i+1, 9):
                pairs.append("%d %d" % (i, j))

        unused = sorted(list(self.find_unused_antennas()))
        legal = []
        for i, u in enumerate(unused):
            for u2 in self.ALL_ANTENNAS:
                if u == u2:
                    continue
                key = "%s %s" % (min(u, u2), max(u, u2))
                if key not in legal:
                    legal.append(key)

        for sec in self.sections():
            values = [item[1] for item in self.items(sec)]
            for i, val in enumerate(values):
                for val2 in values[i+1:]:
                    key = "%s %s" %(min(val, val2),
                                          max(val, val2))
                    if key not in legal:
                        legal.append(key)

        for sec in self.tunnels:
            for antenna, tunnel_val in self.items(sec):
                if antenna.startswith("entrance"):
                    other_cage_antennas = self.other_cage_antenna(tunnel_val)
                    for oca in other_cage_antennas:
                        cage = self.address[oca]
                        values = [item[1] for item in self.items(sec)]
                        for cage_val in values:
                            if cage_val == tunnel_val:
                                continue
                            key = "%s %s" %(min(cage_val, tunnel_val),
                                          max(cage_val, tunnel_val))
                            if key not in legal:
                                legal.append(key)
        for l in legal:
            if l in pairs:
                pairs.remove(l)
        return pairs


class ExperimentConfig(SetupConfig):
    pass