import datetime
import time

import bcrypt
from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

import os

from tornado_sqlalchemy import SQLAlchemy

database_url = os.getenv("Database")

db = SQLAlchemy(database_url)


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    username = Column(Text(), nullable=False, unique=True)
    password = Column(Text(), nullable=False)

    def __repr__(self):
        return f"ID:{self.id}; Username:{self.username}"

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))


class Project(db.Model):
    __tablename__ = "project"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(Text(), nullable=False)
    description = Column(Text(), nullable=False)
    sampleProcessingProtocol = Column(Text(), nullable=False)
    dataProcessingProtocol = Column(Text(), nullable=False)
    experimentType = Column(String(), nullable=False)
    date = Column(DateTime(), nullable=False)
    databaseVersion = Column(String(), nullable=False)
    authors = relationship("Author", back_populates="project", cascade="all, delete-orphan")
    collaborators = relationship("Collaborator", back_populates="project", cascade="all, delete-orphan")
    pis = relationship("PI", back_populates="project", cascade="all, delete-orphan")
    organisms = relationship("Organism", back_populates="project", cascade="all, delete-orphan")
    tissues = relationship("Tissue", back_populates="project", cascade="all, delete-orphan")
    instruments = relationship("Instrument", back_populates="project", cascade="all, delete-orphan")
    cellTypes = relationship("CellType", back_populates="project", cascade="all, delete-orphan")
    diseases = relationship("Disease", back_populates="project", cascade="all, delete-orphan")
    quantificationMethods = relationship("QuantificationMethod", back_populates="project", cascade="all, delete-orphan")
    sampleAnnotations = relationship("SampleAnnotation", back_populates="project", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="project", cascade="all, delete-orphan")
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    comparison = relationship("Comparison", back_populates="project", cascade="all, delete-orphan")
    password = Column(Text(), nullable=True)
    enable = Column(Boolean(), default=False)
    date_created = Column(DateTime(), default=datetime.datetime.utcnow())
    date_updated = Column(DateTime(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return f"ID:{self.id}; Title:{self.title}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            if column.name != "password":
                if column.name.startswith("date"):
                    if column.name == "date":
                        d[column.name] = getattr(self, column.name)
                        d[column.name] = datetime.datetime.utcfromtimestamp(
                            time.mktime(d[column.name].timetuple())).timestamp()
                else:
                    d[column.name] = getattr(self, column.name)
        d["comparison"] = relationship_to_dict(self, "comparison")
        d["authors"] = relationship_to_dict(self, "authors")
        d["collaborators"] = relationship_to_dict(self, "collaborators")
        d["pis"] = relationship_to_dict(self, "pis")
        d["quantificationMethods"] = relationship_to_dict(self, "quantificationMethods")
        d["organisms"] = relationship_to_dict(self, "organisms")
        d["diseases"] = relationship_to_dict(self, "diseases")
        d["keywords"] = relationship_to_dict(self, "keywords")
        d["sampleAnnotations"] = relationship_to_dict(self, "sampleAnnotations")
        d["files"] = relationship_to_dict(self, "files")
        d["instruments"] = relationship_to_dict(self, "instruments")
        d["tissues"] = relationship_to_dict(self, "tissues")
        d["cellTypes"] = relationship_to_dict(self, "cellTypes")
        return d

class Organism(db.Model):
    __tablename__ = "organism"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="organisms")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class Tissue(db.Model):
    __tablename__ = "tissue"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="tissues")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class Instrument(db.Model):
    __tablename__ = "instrument"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="instruments")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class CellType(db.Model):
    __tablename__ = "cellType"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="cellTypes")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class Disease(db.Model):
    __tablename__ = "disease"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="diseases")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class QuantificationMethod(db.Model):
    __tablename__ = "quantificationMethod"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="quantificationMethods")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class Author(db.Model):
    __tablename__ = "author"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    contact = Column(String(), nullable=True)
    first = Column(Boolean(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="authors")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)


class Collaborator(db.Model):
    __tablename__ = "collaborator"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    contact = Column(String(), nullable=True)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="collaborators")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)


class PI(db.Model):
    __tablename__ = "pi"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    contact = Column(String(), nullable=True)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="pis")

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)


class SampleAnnotation(db.Model):
    __tablename__ = "sampleAnnotation"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    description = Column(Text(), nullable=True)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="sampleAnnotations")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class Keyword(db.Model):
    __tablename__ = "keyword"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="keywords")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"


class File(db.Model):
    __tablename__ = "file"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    fileType = Column(String(), nullable=False)
    sampleColumns = relationship("SampleColumn", back_populates="file")
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="files")
    comparisons = relationship("Comparison", back_populates="file")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}; Project ID: {self.project_id}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)

class SampleColumn(db.Model):
    __tablename__ = "sampleColumn"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    columnType = Column(String(), nullable=False)
    file_id = Column(Integer(), ForeignKey("file.id", ondelete="CASCADE"))
    file = relationship("File", back_populates="sampleColumns")
    rawData = relationship("RawData", back_populates="sampleColumn")
    comparison_id = Column(Integer(), ForeignKey("comparison.id", ondelete="CASCADE"))
    comparison = relationship("Comparison", back_populates="sampleColumn")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)

        d["comparison"] = relationship_to_dict(self, "comparison")
        return d


class RawData(db.Model):
    __tablename__ = "rawData"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    primary_id = Column(String(), nullable=False)
    gene_names = Column(String(), nullable=True)
    value = Column(Float(), nullable=True)
    sampleColumn_id = Column(Integer(), ForeignKey("sampleColumn.id", ondelete="CASCADE"))
    sampleColumn = relationship("SampleColumn", back_populates="rawData")

    def __repr__(self):
        return f"ID:{self.id}; Primary_id:{self.primary_id}; Value:{self.value}; Sample Column:{self.sampleColumn}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        d["sampleColumn"] = relationship_to_dict(self, "sampleColumn")
        return d

class DifferentialAnalysisData(db.Model):
    __tablename__ = "differentialAnalysisData"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    primary_id = Column(String(), nullable=False)
    gene_names = Column(String(), nullable=True)
    foldChange = Column(Float(), nullable=True)
    significant = Column(Float(), nullable=True)
    comparison_id = Column(Integer(), ForeignKey("comparison.id", ondelete="CASCADE"))
    comparison = relationship("Comparison", back_populates="differentialAnalysisData", lazy="joined")

    def __repr__(self):
        return f"ID:{self.id}; Primary_id:{self.primary_id}; Fold Change:{self.foldChange}, Significant:{self.significant}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        return d

    def to_dict_df(self):
        d = {}
        for column in self.__table__.columns:
            if not column.name.endswith("id"):
                d[column.name] = getattr(self, column.name)
            elif column.name == "primary_id":
                d[column.name] = getattr(self, column.name)
        d["comparison"] = self.comparison.name
        d["project"] = self.comparison.project.title
        return d

class Comparison(db.Model):
    __tablename__ = "comparison"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    fcColumn = Column(String(), nullable=False)
    significantColumn = Column(String(), nullable=False)
    sampleColumn = relationship("SampleColumn", back_populates="comparison")
    project_id = Column(Integer(), ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="comparison")
    differentialAnalysisData = relationship("DifferentialAnalysisData", back_populates="comparison", lazy="joined")
    file_id = Column(Integer(), ForeignKey("file.id", ondelete="CASCADE"))
    file = relationship("File", back_populates="comparisons")

    def __repr__(self):
        return f"ID:{self.id}; Name:{self.name}; File ID: {self.file_id}"

    def to_dict(self, add_kv={}):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        return d


def create_all_table():
    db.metadata.create_all(db.get_engine())


object_factory_dict = {
    "keywords": Keyword,
    "organisms": Organism,
    "tissues": Tissue,
    "cellTypes": CellType,
    "instruments": Instrument,
    "diseases": Disease,
    "quantificationMethods": QuantificationMethod,
    "authors": Author,
    "sampleAnnotations": SampleAnnotation,
    "files": File,
    "collaborators": Collaborator,
    "pis": PI
}


def create_project_dict(data: dict):
    project = {}
    comparison = {}
    for c in data["comparison"]:
        if "filename" in c:
            if c["filename"] not in comparison:
                comparison[c["filename"]] = []
            comparison[c["filename"]].append(
                Comparison(name=c["name"], fcColumn=c["fc"], significantColumn=c["significant"], sampleColumn=[]))
    for d in data:
        if d != "comparison":
            if d not in object_factory_dict:
                if d == "date":
                    if type(data["date"]) != int:
                        project["date"] = datetime.datetime(data["date"]['year'], data["date"]['month'],
                                                            data["date"]['day'])
                    else:
                        project["date"] = data["date"]

                else:
                    project[d] = data[d]
            else:
                if len(data[d]) > 0:
                    temp = []
                    for i in data[d]:
                        if d == "files":
                            f = File(name=i["name"], fileType=i["fileType"])
                            if f.name in comparison:
                                for c in comparison[f.name]:
                                    c.file = f
                            if "sampleColumns" in i:
                                if len(i["sampleColumns"]) > 0:
                                    cols = []
                                    for c in i["sampleColumns"]:
                                        s = SampleColumn(**c)
                                        if f.name in comparison:
                                            for comp in comparison[f.name]:
                                                if s.columnType == "foldChange":
                                                    if comp.fcColumn == s.name:
                                                        s.comparison = comp
                                                        comp.sampleColumn.append(s)
                                                        break
                                                elif s.columnType == "significant":
                                                    if comp.significantColumn == s.name:
                                                        s.comparison = comp
                                                        comp.sampleColumn.append(s)
                                                        break
                                        cols.append(s)
                                    f.sampleColumns = cols

                            temp.append(f)
                        else:
                            temp.append(object_factory_dict[d](**i))
                    project[d] = temp
    project["comparison"] = []
    for c in comparison:
        project["comparison"] += comparison[c]
    return project


def row2dict(row, columns=[]):
    d = {}
    for column in row.__table__.columns:
        if column.name != "password":
            if len(columns) > 0 and column.name not in columns:
                continue
            d[column.name] = getattr(row, column.name)
            if "date" in column.name:
                if d[column.name]:
                    d[column.name] = d[column.name].timestamp()

    return d


def relationship_to_dict(row, name, columns=[]):
    a = getattr(row, name)
    s = getattr(a, "__table__", False)
    if a != None:
        if s == False:
            return [row2dict(o, columns=columns) for o in a]
        else:
            return row2dict(a, columns=columns)
    return None


def create_password_hash(password):
    hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hash.decode("utf-8")


def update_password(username, password):
    session = db.sessionmaker()
    user = session.query(User).filter(User.username == username).one()
    user.password = create_password_hash(password)
    session.commit()
    session.close()

def create_user(username, password):
    session = db.sessionmaker()
    q = session.query(User.id).filter(User.username == username)
    if session.query(q.exists()).scalar():
        return False
    else:
        session.add(User(username=username, password=create_password_hash(password)))
        session.commit()
    session.close()
    return True

if __name__ == "__main__":
    create_all_table()
    create_user("admin", os.getenv("AdminPassword"))
