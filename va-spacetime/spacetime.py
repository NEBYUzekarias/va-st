from db.interface import *
from opencog.atomspace import AtomSpace, TruthValue
from opencog.atomspace import types
from opencog.type_constructors import *
from opencog.scheme_wrapper import scheme_eval_h, scheme_eval_as


class SpaceTimeServer:
    def __init__(self):
        self.db = Database()
        self.space = scheme_eval_as('(cog-atomspace)')

    def add_atom(self,atom):
        location = atom.get_value(PredicateNode("location"))
        if location:
            location = location.to_list()
        timestamp = atom.get_value(PredicateNode("timestamp"))
        if timestamp:
            timestamp = timestamp.to_list()[0]
        self.db.add_atom(atom=atom, longitude=location[0], latitude=location[1], time=timestamp)
        return TruthValue(1.0,1.0)

    def get_atom_by_time(self, time):
        timestamp = float(time.name)
        return scheme_eval_h(self.space, self.db.get_atom_by_time(timestamp).atom)

    def get_atom_by_location(self, longitude, latitude):
        return scheme_eval_h(self.space, self.db.get_atom_by_location(float(longitude.name), float(latitude.name)).atom)

    def get_nearest_neighbors(self,longitude, latitude, distance):
        longitude = float(longitude.name)
        latitude = float(latitude.name)
        distance = float(distance.name)
        result = self.db.get_nearest_neighbors(longitude, latitude, distance)
        nearest = list(map(lambda r: scheme_eval_h(self.space, r.atom), result))
        return SetLink(*nearest)

    def get_location_by_time(self, time):
        time = float(time.name)
        result = self.db.get_location(time)
        atom = scheme_eval_h(self.space, result[0].atom)
        r = EvaluationLink(
                    PredicateNode("locatedAt"),
                    ListLink(
                        atom,
                        NumberNode(str(result[1])),
                        NumberNode(str(result[2]))))
        return r
if __name__ == "__main__":
    GroundedObjectNode("spatio-temporal-index", SpaceTimeServer())
