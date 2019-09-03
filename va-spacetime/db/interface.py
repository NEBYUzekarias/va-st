from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Integer, String,DateTime
from sqlalchemy.sql import cast
from geoalchemy2 import *
from datetime import datetime

Base = declarative_base()

class SpaceTime(Base):
    __tablename__ = 'spacetime'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime,default=datetime.utcnow)
    location = Column(Geography(geometry_type='POINT', dimension=2,srid=4326))
    atom = Column(String)

    def __init__(self, longitude, latitude, atom, time):
        self.time = datetime.fromtimestamp(time) if time else datetime.utcnow
        self.atom = str(atom)
        if latitude and longitude:
            self.location = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)

    def __repr__(self):
        return "Atom      : {}\n"\
               "Location  : {}\n"\
               "time      : {}\n".format(self.atom,
                                         self.location,
                                         self.time)

class Database:
    def __init__(self, username="admin", password="admin", database="spacetime", host="localhost", port=5432):
        self.db = 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host,port, database)
        self.engine = create_engine(self.db)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    def _create(self, drop=False):
        if drop:
            Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def drop(self):
         Base.metadata.drop_all(bind=self.engine)

    def _query_table(self, *table):
        return self.session.query(*table)

    def _query(self,result, order=None, geo_filter=None, **filters):
        if filters:
            result = result.filter(geo_filter) if geo_filter else result.filter_by(**filters).order_by(order)
        return result

    def add_atom(self, longitude,latitude, atom, time):
        try:
            s = SpaceTime(atom=atom, longitude=longitude,latitude=latitude, time=time)
            self.session.add(s)
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()

    def get_atom_by_time(self, time):
        r = self._query_table(SpaceTime)
        return self._query(result=r, time = datetime.fromtimestamp(time)).first()

    def get_atom_by_location(self,longitude, latitude):
        r = self._query_table(SpaceTime)
        return self._query(result=r, location=Database._format_location(longitude, latitude)).first()

    def get_nearest_neighbors(self, longitude, latitude, distance = 0):
        r =  self._query_table(SpaceTime)
        if distance:
            return self._query(result=r, geo_filter= Database.within_clause(longitude, latitude, distance)).all()
        return self._query(result=r, order=Database.distance_clause(longitude, latitude)).limit(3).all()

    def get_distance(self, longitude, latitude):
        return self._query_table(SpaceTime, Database.distance_clause(longitude, latitude)).all()

    def get_location(self, time):
        r = self._query_table(SpaceTime, func.ST_X(Database._cast_location(Geometry)), func.ST_Y(Database._cast_location(Geometry)))
        return self._query(result=r, time = datetime.fromtimestamp(time)).first()

    @staticmethod
    def _format_location(longitude, latitude):
        return 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)

    @staticmethod
    def _cast_location(type):
        return cast(SpaceTime.location, type)

    @staticmethod
    def within_clause(latitude, longitude, distance=10):
        location = Database._format_location(longitude=longitude, latitude=latitude)
        return func.ST_DWithin(SpaceTime.location, location, distance)

    @staticmethod
    def distance_clause(longitude, latitude):
        location = Database._format_location(longitude=longitude, latitude=latitude)
        return func.ST_Distance(SpaceTime.location, location)
