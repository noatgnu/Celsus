import datetime
import os
from unittest import TestCase

os.environ["Database"] = "sqlite://"
from celsus.models import create_project_dict


from celsus import models

models.db.metadata.create_all(models.db.get_engine())

class TestSampleAnnotation(TestCase):
    def test_sampleAnnotation(self):
        session = models.db.sessionmaker()
        sa = models.SampleAnnotation(name="test", description="test")
        print(sa)
        session.add(sa)
        session.commit()
        sa_list = session.query(models.SampleAnnotation).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.SampleAnnotation).all()
        assert len(sa_list) == 0


class TestAuthors(TestCase):
    def test_author(self):
        session = models.db.sessionmaker()
        sa = models.Author(name="test", contact="test@test.edu", first=True)
        session.add(sa)
        session.commit()
        sa_list = session.query(models.Author).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.Author).all()
        assert len(sa_list) == 0


class TestQuantificationMethod(TestCase):
    def test_quantificationMethod(self):
        session = models.db.sessionmaker()
        sa = models.QuantificationMethod(name="test")
        session.add(sa)
        session.commit()
        sa_list = session.query(models.QuantificationMethod).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.QuantificationMethod).all()
        assert len(sa_list) == 0


class TestDisease(TestCase):
    def test_disease(self):
        session = models.db.sessionmaker()
        sa = models.Disease(name="test")
        session.add(sa)
        session.commit()
        sa_list = session.query(models.Disease).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.Disease).all()
        assert len(sa_list) == 0


class TestCellType(TestCase):
    def test_cell_type(self):
        session = models.db.sessionmaker()
        sa = models.CellType(name="test")
        session.add(sa)
        session.commit()
        sa_list = session.query(models.CellType).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.CellType).all()
        assert len(sa_list) == 0

class TestInstrument(TestCase):
    def test_instrument(self):
        session = models.db.sessionmaker()
        sa = models.Instrument(name="test")
        session.add(sa)
        session.commit()
        sa_list = session.query(models.Instrument).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.Instrument).all()
        assert len(sa_list) == 0


class TestTissue(TestCase):
    def test_tissue(self):
        session = models.db.sessionmaker()
        sa = models.Tissue(name="test")
        session.add(sa)
        session.commit()
        sa_list = session.query(models.Tissue).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.Tissue).all()
        assert len(sa_list) == 0


class TestOrganism(TestCase):
    def test_organism(self):
        session = models.db.sessionmaker()
        sa = models.Organism(name="test")
        session.add(sa)
        session.commit()
        sa_list = session.query(models.Organism).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.Organism).all()
        assert len(sa_list) == 0

class TestKeyword(TestCase):
    def test_keyword(self):
        session = models.db.sessionmaker()
        sa = models.Keyword(name="test")
        session.add(sa)
        session.commit()
        sa_list = session.query(models.Keyword).all()
        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.Keyword).all()
        assert len(sa_list) == 0

class TestProject(TestCase):
    def test_project(self):
        session = models.db.sessionmaker()
        organisms = [
            models.Organism(name="test1"),
            models.Organism(name="test2"),
            models.Organism(name="test3"),
        ]
        tissues = [
            models.Tissue(name="test1"),
            models.Tissue(name="test2"),
            models.Tissue(name="test3"),
        ]
        instruments = [
            models.Instrument(name="test1"),
            models.Instrument(name="test2"),
            models.Instrument(name="test3"),
        ]
        quants = [
            models.QuantificationMethod(name="test1"),
            models.QuantificationMethod(name="test2"),
            models.QuantificationMethod(name="test3"),
        ]
        samnote = [
            models.SampleAnnotation(name="test1", description="test1"),
            models.SampleAnnotation(name="test2", description="test2"),
            models.SampleAnnotation(name="test3", description="test3"),
        ]
        diseases = [
            models.Disease(name="test1"),
            models.Disease(name="test2"),
            models.Disease(name="test3"),
        ]
        cells = [
            models.CellType(name="test1"),
            models.CellType(name="test2"),
            models.CellType(name="test3"),
        ]
        authors = [
            models.Author(name="test1", contact="test1@test1.edu", first=True),
            models.Author(name="test2", contact="test1@test2.edu", first=False),
            models.Author(name="test3", contact="test1@test3.edu", first=False),
        ]
        keywords = [
            models.Keyword(name="test1"),
            models.Keyword(name="test2"),
            models.Keyword(name="test3"),
        ]
        project = models.Project(title="testProject",
                                 description="testDescription",
                                 sampleProcessingProtocol="testProtocol",
                                 dataProcessingProtocol="testProtocol",
                                 experimentType="test",
                                 databaseVersion="01",
                                 date=datetime.datetime.utcnow(),
                                 authors=authors,
                                 organisms=organisms,
                                 tissues=tissues,
                                 instruments=instruments,
                                 cellTypes=cells,
                                 diseases=diseases,
                                 sampleAnnotations=samnote,
                                 quantificationMethods=quants,
                                 keywords=keywords
                                 )
        session.add(project)
        session.commit()
        sa_list = session.query(models.Project).all()

        assert len(sa_list) == 1
        for s in sa_list:
            session.delete(s)
        session.commit()
        sa_list = session.query(models.Project).all()

        assert len(sa_list) == 0
        author = session.query(models.Author).all()

        assert len(author) == 0

    def test_patch(self):
        req = {
              "username": "admin",
              "project": {
                "id": 1,
                "title": "test",
                "description": "<p>asdveafv</p>",
                "sampleProcessingProtocol": "<p>dfbasdv</p>",
                "dataProcessingProtocol": "<p>rgbdfg</p>",
                "experimentType": "Cross-linking (CX-MS)",
                "date": {
                  "day": 5,
                  "month": 6,
                  "year": 2022
                },
                "databaseVersion": "bfs",
                "enable": True,
                "comparison": [
                  {
                    "fc": "Difference: Wt/KO (Log2)",
                    "significant": "P-Value (-Log10)",
                    "filename": "SGK3_Wt_KO_TP.txt",
                    "name": "testest"
                  }
                ],
                "authors": [
                  {
                    "id": 1,
                    "name": "setd",
                    "contact": "fset",
                    "first": True,
                    "project_id": 1
                  }
                ],
                "collaborators": [
                  {
                    "id": 1,
                    "name": "dsfg",
                    "contact": "svfd",
                    "project_id": 1
                  }
                ],
                "pis": [
                  {
                    "id": 1,
                    "name": "sefv",
                    "contact": "sdvfb",
                    "project_id": 1
                  }
                ],
                "quantificationMethods": [
                  {
                    "id": 1,
                    "name": "gfdn",
                    "project_id": 1
                  }
                ],
                "organisms": [
                  {
                    "id": 1,
                    "name": "asdfb",
                    "project_id": 1
                  }
                ],
                "diseases": [
                  {
                    "id": 1,
                    "name": "hngf",
                    "project_id": 1
                  }
                ],
                "keywords": [
                  {
                    "id": 1,
                    "name": "dsvf",
                    "project_id": 1
                  }
                ],
                "sampleAnnotations": [
                  {
                    "id": 1,
                    "name": "bgd",
                    "description": "dfgbn",
                    "project_id": 1
                  }
                ],
                "files": [
                  {
                    "name": "SGK3_Wt_KO_TP.txt",
                    "fileType": "Differential analysis",
                    "sampleColumns": [
                      {
                        "name": "Majority protein IDs",
                        "columnType": "primaryID"
                      },
                      {
                        "name": "Difference: Wt/KO (Log2)",
                        "columnType": "foldChange"
                      },
                      {
                        "name": "P-Value (-Log10)",
                        "columnType": "significant"
                      }
                    ]
                  }
                ],
                "instruments": [
                  {
                    "id": 1,
                    "name": "treb",
                    "project_id": 1
                  }
                ],
                "tissues": [
                  {
                    "id": 1,
                    "name": "dsfb",
                    "project_id": 1
                  }
                ],
                "cellTypes": [
                  {
                    "id": 1,
                    "name": "fevs",
                    "project_id": 1
                  }
                ]
              },
              "updateProperties": [
                "files",
                "comparison"
              ]
            }
        session = models.db.sessionmaker()
        project = models.Project(**create_project_dict(req["project"]))
        session.add(project)
        session.commit()
        print(project.comparison[0].to_dict())
        project = session.query(models.Project).filter(models.Project.id == req["project"]["id"]).one()
        comparison = {}

        for i in req["updateProperties"]:
            print(i)
            if i not in models.object_factory_dict:
                if i == "comparison":
                    project.comparison = []
                    for c in req["project"][i]:
                        if "filename" in c:
                            if c["filename"] not in comparison:
                                comparison[c["filename"]] = []
                        elif "file_id" in c:

                            o = session.query(models.File).filter(
                                models.File.id == c["file_id"]).one()
                            comparison[o.name] = []
                        if "id" in c:
                            o = session.query(models.Comparison).filter(
                                models.Comparison.id == c["id"]).one()
                            for k in c:
                                if k != "id":
                                    setattr(o, k, c[k])
                            o.sampleColumns = []
                            comparison[o.file.name].append(o)
                        else:
                            for f in project.files:
                                if f.name == c["filename"]:
                                    o = models.Comparison(name=c["name"], fcColumn=c["fc"],
                                                          significantColumn=c["significant"])
                                    o.project = project
                                    o.file = f
                                    break
                        project.comparison.append(o)

                elif i != "date":
                    setattr(project, i, req["project"][i])


                else:
                    setattr(project, i, datetime(req["project"]["date"]['year'], req["project"]["date"]['month'],
                                                 req["project"]["date"]['day']))
            else:
                files = []
                for a in req["project"][i]:
                    if "id" in a:
                        o = session.query(models.object_factory_dict[i]).filter(
                            models.object_factory_dict[i].id == a["id"]).one()
                        for k in a:
                            if k != "id":
                                if type(a[k]) is not dict and type(a[k]) is not list:
                                    setattr(o, k, a[k])

                    else:

                        o = models.object_factory_dict[i]()
                        for k in a:
                            if type(a[k]) is not dict and type(a[k]) is not list:
                                setattr(o, k, a[k])
                        session.add(o)
                        files.append(o)
                    # if i == "files":
                    #     if o.name in comparison:
                    #         for c in comparison[o.name]:
                    #             if o.name not in comparison_object:
                    #                 comparison_object[o.name] = []
                    #                 c.file = o.id
                    #                 c.project_id = project.id
                    #             comparison_object[o.name].append(c)
                    #         if o.name in comparison_object:
                    #             o.comparisons = comparison_object[o.name]
                    #     files.append(o)

                if i == "files":
                    for f in files:
                        f.project_id = project.id
                    project.files = files
                    # if f.name in comparison:
                    #     for c in comparison[o.name]:
                    #         if f.name not in comparison_object:
                    #             print(f)
                    #             comparison_object[f.name] = []
                    #             c.file_id = f.id
                    #             session.commit()
                    #         comparison_object[f.name].append(f)

                    # if len(a["sampleColumns"]) > 0:
                    #     cols = []
                    #     for s in a["sampleColumns"]:
                    #         if "id" in s:
                    #             sa = session.query(models.SampleColumn).filter(
                    #                 models.SampleColumn.id == s["id"]).one()
                    #             for k in s:
                    #                 if k != "id":
                    #                     if type(s[k]) is not dict and type(s[k]) is not list:
                    #                         setattr(sa, k, s[k])
                    #         else:
                    #             sa = models.SampleColumn(**s)
                    #             session.add(sa)
                    #             session.commit()
                    #         if o.name in comparison:
                    #             for comp in comparison[o.name]:
                    #                 if sa.columnType == "foldChange":
                    #                     if comp.fcColumn == sa.name:
                    #                         sa.comparison = comp
                    #                         sa.file = o
                    #                         comp.sampleColumn.append(sa)
                    #                         break
                    #                 elif sa.columnType == "significant":
                    #                     if comp.significantColumn == sa.name:
                    #                         sa.comparison = comp
                    #                         sa.file = o
                    #                         comp.sampleColumn.append(sa)
                    #                         break
                    #         cols.append(sa)
                    #     o.sampleColumns = cols
                    # data_array.append(o)
                    # print(o)

                # print(i)
                # print(data_array)
                # setattr(project, i, data_array)
        print(project)
        session.commit()

        print(project)


