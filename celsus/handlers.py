import gzip
import io
import os
import secrets
import subprocess
import sys
import urllib.parse
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from operator import and_

from sqlalchemy import or_, desc
from tornado import gen, iostream
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from tornado.web import RequestHandler, stream_request_body
from tornado_sqlalchemy import SessionMixin
from uniprotparser.parser import UniprotSequence, UniprotParser

import settings
from celsus import models
from celsus.models import Project, create_project_dict, row2dict, RawData, DifferentialAnalysisData
import pandas as pd

from celsus.pagination import Page
from bson import ObjectId
temp_cache = dict()

class BaseHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Access-control-allow-origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "x-requested-with,Access-control-allow-origin,authorization,content-type,unique-id,filename,access-token"
                        )
        self.set_header("Access-Control-Expose-Headers", "Access-Token")
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH')

    def options(self):
        self.set_status(204)
        self.finish()


class ProjectHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def post(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            d = create_project_dict(req)
            project = Project(**d)
            session.add(project)
            session.commit()
            self.write(row2dict(project))

    @gen.coroutine
    def get(self, project_id):
        with self.make_session() as session:
            if project_id == "0":
                results = session.query(models.Project).order_by(desc(models.Project.date_created)).limit(5).all()
                self.write({"results": [r.to_dict() for r in results]})
            else:
                ids = project_id.split(",")
                results = session.query(models.Project).filter(or_(*[models.Project.id == int(i) for i in ids])).all()
                self.write({"results": [r.to_dict() for r in results]})

    @gen.coroutine
    def patch(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            access_token = self.request.headers.get("Access-Token")
            token = yield self.application.redis.get(req["username"])
            if token.decode("utf-8") == access_token:
                project = session.query(models.Project).filter(models.Project.id == req["project"]["id"]).one()
                new_project = create_project_dict(req["project"])
                comparison = {}
                for i in req["updateProperties"]:
                    print(i)
                    if i not in models.object_factory_dict:
                        if i == "comparison":
                            for c in range(len(new_project["comparison"])):
                                new_project["comparison"][c].project_id = project.id
                                #new_project["comparison"][c].file = None
                            project.comparison = new_project["comparison"]
                            pass
                        elif i != "date":
                            setattr(project, i, req["project"][i])
                        else:
                            setattr(project, i, datetime(req["project"]["date"]['year'], req["project"]["date"]['month'],
                                              req["project"]["date"]['day']))
                    else:
                        if i == "files":
                            file_map = {}
                            for c in range(len(new_project["files"])):
                                new_project["files"][c].project_id = project.id
                                new_project["files"][c].comparisons = []
                                file_map[new_project["files"][c].name] = new_project["files"][c]

                            for f in project.files:
                                if f.name in file_map:
                                    if file_map[f.name].fileType == f.fileType:
                                        file_map[f.name] = f
                            setattr(project, i, [file_map[k] for k in file_map])
                        else:
                            setattr(project, i, new_project[i])
                        # files = []
                        # for a in req["project"][i]:
                        #     if "id" in a:
                        #         o = session.query(models.object_factory_dict[i]).filter(models.object_factory_dict[i].id == a["id"]).one()
                        #         for k in a:
                        #             if k != "id":
                        #                 if type(a[k]) is not dict and type(a[k]) is not list:
                        #                     setattr(o, k, a[k])
                        #
                        #     else:
                        #
                        #         o = models.object_factory_dict[i]()
                        #         for k in a:
                        #             if type(a[k]) is not dict and type(a[k]) is not list:
                        #                 setattr(o, k, a[k])
                        #         session.add(o)
                        #         files.append(o)
                        #     # if i == "files":
                        #     #     if o.name in comparison:
                        #     #         for c in comparison[o.name]:
                        #     #             if o.name not in comparison_object:
                        #     #                 comparison_object[o.name] = []
                        #     #                 c.file = o.id
                        #     #                 c.project_id = project.id
                        #     #             comparison_object[o.name].append(c)
                        #     #         if o.name in comparison_object:
                        #     #             o.comparisons = comparison_object[o.name]
                        #     #     files.append(o)
                        #
                        # if i == "files":
                        #     for f in files:
                        #         f.project_id = project.id
                        #     project.files = files
                        #         # if f.name in comparison:
                        #         #     for c in comparison[o.name]:
                        #         #         if f.name not in comparison_object:
                        #         #             print(f)
                        #         #             comparison_object[f.name] = []
                        #         #             c.file_id = f.id
                        #         #             session.commit()
                        #         #         comparison_object[f.name].append(f)
                        #
                        #     # if len(a["sampleColumns"]) > 0:
                        #     #     cols = []
                        #     #     for s in a["sampleColumns"]:
                        #     #         if "id" in s:
                        #     #             sa = session.query(models.SampleColumn).filter(
                        #     #                 models.SampleColumn.id == s["id"]).one()
                        #     #             for k in s:
                        #     #                 if k != "id":
                        #     #                     if type(s[k]) is not dict and type(s[k]) is not list:
                        #     #                         setattr(sa, k, s[k])
                        #     #         else:
                        #     #             sa = models.SampleColumn(**s)
                        #     #             session.add(sa)
                        #     #             session.commit()
                        #     #         if o.name in comparison:
                        #     #             for comp in comparison[o.name]:
                        #     #                 if sa.columnType == "foldChange":
                        #     #                     if comp.fcColumn == sa.name:
                        #     #                         sa.comparison = comp
                        #     #                         sa.file = o
                        #     #                         comp.sampleColumn.append(sa)
                        #     #                         break
                        #     #                 elif sa.columnType == "significant":
                        #     #                     if comp.significantColumn == sa.name:
                        #     #                         sa.comparison = comp
                        #     #                         sa.file = o
                        #     #                         comp.sampleColumn.append(sa)
                        #     #                         break
                        #     #         cols.append(sa)
                        #     #     o.sampleColumns = cols
                        #     #data_array.append(o)
                        #     #print(o)
                        #
                        # #print(i)
                        # #print(data_array)
                        # #setattr(project, i, data_array)
                print(project)
                session.commit()

                self.write({"results": [project.to_dict()]})


@stream_request_body
class UploadHandler(SessionMixin, BaseHandler, ABC):
    def initialize(self):
        self.byte_read = 0

    @gen.coroutine
    def data_received(self, chunk):
        if "open_file" not in self.__dict__:
            print(self.request.headers)
            uniqueID = self.request.headers.get("Unique-ID")
            self.filename = self.request.headers.get("Filename")
            self.folder_path = os.path.join(settings.location, uniqueID)
            os.makedirs(self.folder_path, exist_ok=True)
            os.makedirs(os.path.join(self.folder_path, "temp"), exist_ok=True)
            os.makedirs(os.path.join(self.folder_path, "data"), exist_ok=True)
            self.path = os.path.join(self.folder_path, "temp", self.filename)
            self.open_file = open(self.path, "wb")
            self.project_id = int(uniqueID)

        self.open_file.write(chunk)
        self.byte_read += len(chunk)

    @gen.coroutine
    def put(self):
        # mtype = self.request.headers.get("Content-Type")
        # logging.info('PUT "%s" "%s" %d bytes', filename, mtype, self.bytes_read)
        self.open_file.close()
        fin_path = os.path.join(self.folder_path, "data", self.filename)
        if sys.platform.startswith("win32"):
            with open(self.path, "rt") as tempfile, \
                    open(fin_path, "wt", newline="") as datafile:
                boundary_pass = False
                for line in tempfile:
                    templine = line.strip()
                    if templine.startswith("------WebKitFormBoundary"):
                        if boundary_pass == True:
                            break
                        continue
                    elif templine.startswith("Content-"):
                        continue
                    elif templine == "" and boundary_pass == False:
                        boundary_pass = True
                        continue
                    else:
                        datafile.write(line)
        else:
            p1 = subprocess.Popen(["tail", "-n", "+5", self.path], stdout=subprocess.PIPE)
            with open(fin_path, "wb") as datafile:
                subprocess.run(["head", "-n", "-2"], stdin=p1.stdout, stdout=datafile)
        with self.make_session() as session:
            file = session.query(models.File)\
                .filter(and_(models.File.project_id == self.project_id, models.File.name == self.filename)).all()
            if file[0].fileType == "Differential analysis":
                self.comparison = session.query(models.Comparison)\
                    .filter(models.Comparison.project_id == self.project_id).all()
            yield self.process_file(file[0], fin_path)
            session.commit()
            self.write(row2dict(file[0]))

    @gen.coroutine
    def process_file(self, file, fin_path):
        if file.fileType != "Other":
            if fin_path.endswith("txt") or fin_path.endswith("tsv"):
                df = pd.read_csv(fin_path, sep="\t")
            else:
                df = pd.read_csv(fin_path)
            column_dict = {}
            for c in file.sampleColumns:
                if c.columnType not in column_dict:
                    column_dict[c.columnType] = []
                column_dict[c.columnType].append(c)
            if file.fileType == "Raw":
                for c in column_dict["sample"]:
                    rawDataList = []
                    new_df = df[[column_dict["primaryID"][0].name, c.name]]
                    new_df.rename(columns={column_dict["primaryID"][0].name: "primary_id", c.name: "value"},
                                  inplace=True)

                    result = yield get_uniprot(new_df["primary_id"], self.application.redis)

                    for i in new_df.to_dict('records'):
                        r = RawData(**i)
                        if r.primary_id in temp_cache:
                            r.gene_names = temp_cache[r.primary_id]
                        else:
                            for p in r.primary_id.split(";"):
                                a = result.get_accession_from_query(p)
                                a = a.accession
                                if a:
                                    temp = result.df[result.df["query"] == a]
                                    if type(temp) == pd.Series:
                                        r.gene_names = temp["Gene names"]
                                        break
                                    elif type(temp) == pd.DataFrame:
                                        if len(temp) > 0:
                                            for _, r2 in temp.iterrows():
                                                r.gene_names = r2["Gene names"]
                                                temp_cache[r.primary_id] = r2["Gene names"]
                                                break
                                            break
                        rawDataList.append(r)
                    c.rawData.extend(rawDataList)
            elif file.fileType == "Differential analysis":

                for comp in self.comparison:
                    differentialAnalysisList = []
                    analysis = {"primary": column_dict["primaryID"][0]}
                    for sa in comp.sampleColumn:
                        if sa.name == comp.fcColumn:
                            analysis["fc"] = sa
                        elif sa.name == comp.significantColumn:
                            analysis["significant"] = sa
                    new_df = df[[analysis["primary"].name, analysis["fc"].name, analysis["significant"].name]]

                    new_df.rename(columns={analysis["primary"].name: "primary_id", analysis["fc"].name: "foldChange", analysis["significant"].name: "significant"}, inplace=True)
                    result = yield get_uniprot(new_df["primary_id"], self.application.redis)
                    for i in new_df.to_dict('records'):
                        r = DifferentialAnalysisData(**i)
                        if r.primary_id in temp_cache:
                            r.gene_names = temp_cache[r.primary_id]
                        else:
                            for p in r.primary_id.split(";"):
                                a = result.get_accession_from_query(p)
                                a = a.accession
                                if a:
                                    temp = result.df[result.df["query"] == a]
                                    if type(temp) == pd.Series:
                                        r.gene_names = temp["Gene names"]
                                        temp_cache[r.primary_id] = r.gene_names

                                        break
                                    elif type(temp) == pd.DataFrame:
                                        if len(temp) > 0:
                                            for _, r2 in temp.iterrows():
                                                r.gene_names = r2["Gene names"]
                                                temp_cache[r.primary_id] = r2["Gene names"]
                                                break
                                            break
                        differentialAnalysisList.append(r)
                    comp.differentialAnalysisData.extend(differentialAnalysisList)


class SearchDifferentialAnalysisHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def post(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            primary_ids = ["%{}%".format(t) for t in req["term"]]
            results = {"results": []}
            prime_model = session.query(models.DifferentialAnalysisData).join(models.Comparison).join(models.Project)
            if not req["ignoreAvailability"]:
                prime_model = prime_model.filter(models.Project.enable == True)
            print(primary_ids)
            if len(primary_ids) == 1:
                model = prime_model.filter(
                    or_(
                        *[
                            models.DifferentialAnalysisData.primary_id.ilike(primary_ids[0].upper()),
                            models.DifferentialAnalysisData.gene_names.ilike(primary_ids[0])
                        ]
                    )
                )

                # if len(results["results"]) == 0:
                #     #primary_ids = yield self.check_UniProt(primary_ids)
                #     model = prime_model.filter(
                #         or_(*[models.DifferentialAnalysisData.primary_id.like(pid) for pid in primary_ids])
                #     ).filter(or_(*[models.DifferentialAnalysisData.gene_names.like(pid) for pid in primary_ids]))
            elif len(primary_ids) == 0:
                model = prime_model
                results["unique_primary_ids"] = [r[0] for r in model.with_entities(
                    models.DifferentialAnalysisData.primary_id).distinct().all()]
                #results["unique_comparison"] = [r.to_dict() for r in
                #                                model.with_entities(models.Comparison).distinct().all()]
                #results["unique_primary_ids"] = [r[0] for r in model.with_entities(
                #    models.DifferentialAnalysisData.primary_id).distinct().all()]
                #results["unique_gene_names"] = [r[0] for r in model.with_entities(
                #    models.DifferentialAnalysisData.gene_names).distinct().all()]

                #primary_ids = yield self.check_UniProt(results["unique_primary_ids"])

            else:
                #primary_ids = yield self.check_UniProt(primary_ids)
                conditions = [models.DifferentialAnalysisData.primary_id.ilike(pid) for pid in primary_ids]
                conditions = conditions + [models.DifferentialAnalysisData.gene_names.ilike(pid) for pid in primary_ids]
                model = prime_model.filter(
                    or_(*conditions)
                )

            filter_condition_primary = []
            filter_condition_comparison = []
            filter_condition_project = []
            filter_condition_gene = []
            for k in req["filter"]:
                if len(req["filter"][k]) > 0:

                    if k == "primary_id":
                        filter_condition_primary = filter_condition_primary + [models.DifferentialAnalysisData.primary_id == pid for pid in req["filter"][k]]

                    elif k == "comparison_id":
                        filter_condition_comparison = filter_condition_comparison + [models.DifferentialAnalysisData.comparison_id == int(compid) for compid in req["filter"][k]]

                    elif k == "project_id":
                        filter_condition_project = filter_condition_project + [models.Comparison.project_id == pid for pid in req["filter"][k]]

                    elif k == "gene_names":
                        filter_condition_gene = filter_condition_gene + [models.DifferentialAnalysisData.gene_names == pid for pid in req["filter"][k]]
            if len(filter_condition_primary) > 0:
                model = model.filter(or_(*filter_condition_primary))
            if len(filter_condition_project) > 0:
                model = model.filter(or_(*filter_condition_project))
            if len(filter_condition_comparison) > 0:
                model = model.filter(or_(*filter_condition_comparison))
            if len(filter_condition_gene) > 0:
                model = model.filter(or_(*filter_condition_gene))
            if req["type"] == "initial search":
                results["unique_project_ids"] = [r[0] for r in
                                                 model.with_entities(models.Comparison.project_id).distinct().all()]
                results["unique_comparison"] = [r.to_dict() for r in
                                                model.with_entities(models.Comparison).distinct().all()]
                results["unique_primary_ids"] = [r[0] for r in model.with_entities(
                    models.DifferentialAnalysisData.primary_id).distinct().all()]
                results["unique_gene_names"] = [r[0] for r in model.with_entities(
                    models.DifferentialAnalysisData.gene_names).distinct().all()]

            if "format" in req:
                if req["format"] == "txt":
                    df = []
                    for m in model.all():
                        df.append(m.to_dict_df())

                    df = pd.DataFrame(df)

                    token = secrets.token_urlsafe()
                    yield self.application.redis.set(token, df.to_csv(sep="\t"), 60*60*24)
                    print(token)
                    self.write({"results": [], "download-token": token})
                    self.flush()
                else:
                    page = Page(model, req["page"], req["per_page"])
                    results["results"] = page.values()
                    results["total_pages"] = page.total_pages()
                    results["count"] = page.count()
                    results["gene_name_map"] = {}
                    dict_result = []
                    for r in results["results"]:
                        m = r.to_dict()
                        results["gene_name_map"][m["primary_id"]] = m["gene_names"]
                        dict_result.append(m)
                    if "all" in req:
                        if req["all"]:
                            result_all = model.all()
                            dict_all_result = []
                            for r in result_all:
                                dict_all_result.append(r.to_dict())
                            results["all_results"] = dict_all_result
                    results["results"] = dict_result
                    self.write(results)

    @gen.coroutine
    def check_UniProt(self, primary_ids: list[str]):
        client = AsyncHTTPClient()
        data = []
        total = len(primary_ids)
        request = "https://rest.uniprot.org/idmapping/run"
        client = AsyncHTTPClient()
        body = urllib.parse.urlencode({
            "ids": ",".join(primary_ids).replace("; ", ""),
            "from": "UniProtKB_AC-ID",
            "to": "UniProtKB",
            "columns": "id,entry name,genes"
        })
        r = HTTPRequest(request, "POST", headers={"accept-encoding": "gzip, deflate, br"}, body=body)
        if request not in temp_cache:
            response = yield client.fetch(r)
            job = json_decode(response.body.decode("utf-8"))
            status_request = "https://rest.uniprot.org/idmapping/status/{}".format(job["jobId"], "GET")
            while True:
                res = yield client.fetch(status_request)
                if res.code != 303:
                    break
                yield gen.sleep(1)
            finshed = HTTPRequest("https://rest.uniprot.org/idmapping/uniprotkb/results/{}/?format=tsv".format(job["jobId"]), "GET")
            res = yield client.fetch(finshed)
            gzip_f = gzip.GzipFile(fileobj=BytesIO(res.body))
            temp_cache[body] = pd.read_csv(gzip_f, sep="\t")
            #temp_cache[body].rename(columns={temp_cache[request].column[-1]:"query"}, inplace=True)

        data = temp_cache[body]

        data["Gene Names"] = data["Gene Names"].str.upper()
        data["Gene Names"] = data["Gene Names"].str.replace(";", "")
        data["Gene Names Split"] = data["Gene Names"].str.split()
        data.to_csv("test.csv")
        data = data.explode("Gene Names Split")
        #data = data[data["Gene Names Split"].isin(primary_ids)|data["Entry"].isin(primary_ids)]
        self.gene_names_map = {r["Entry"]:r["Gene Names Split"] for _, r in data.iterrows()}

        return [e for e in data["Entry"].values]


class FileDownloadHandler(BaseHandler, ABC):
    @gen.coroutine
    def get(self, project_id, filename):
        self.set_header("Content-Type", "text/plain")
        self.set_header("Content-Disposition", "attachment; filename={}".format(urllib.parse.quote(filename)))
        file_path = os.path.join(settings.location, project_id, "data", filename)
        chunk_size = 1024 * 1024 * 1
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    try:
                        self.write(chunk)
                        yield self.flush()
                    except iostream.StreamClosedError:
                        break
                    finally:
                        del chunk
                        yield gen.sleep(0.000000001)

    @gen.coroutine
    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.set_header("Content-Disposition", "attachment; filename={}".format(urllib.parse.quote("data.txt")))


class DownloadTokenHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def get(self, token):
        self.set_header("Content-Type", "text/plain")
        self.set_header("Content-Disposition", "attachment; filename={}".format(urllib.parse.quote("data.txt")))
        file = yield self.application.redis.get(token)
        print(file)
        if file:
            self.write(file)
            # chunk_size = 1024 * 1024 * 1
            # while True:
            #     chunk = BytesIO(file).read(chunk_size)
            #     if not chunk:
            #         break
            #     try:
            #         self.write(chunk)
            #         yield self.flush()
            #     except iostream.StreamClosedError:
            #         break
            #     finally:
            #         del chunk
            #         yield gen.sleep(0.000000001)


class FileColumnHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def post(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            access_token = self.request.headers.get("Access-Token")
            token = yield self.application.redis.get(req["username"])
            file_path = os.path.join(settings.location, str(req["file"]["project_id"]), "data", req["file"]["name"])
            if token.decode("utf-8") == access_token:
                sampleColumns = session.query(models.SampleColumn).filter(models.SampleColumn.file_id == req["file"]["id"]).all()
                with open(file_path, "rt") as data:
                    for i in data:
                        self.write({"results": i.strip().replace("\"", "").split("\t"), "sampleColumns": [r.to_dict() for r in sampleColumns]})
                        break

class ComparisonHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def post(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            access_token = self.request.headers.get("Access-Token")
            token = yield self.application.redis.get(req["username"])


class AuthorHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def get(self, search):
        with self.make_session() as session:
            result = session.query(models.Author.name.ilike("%{}%".format(search))).limit(10).all()
            self.write({"results": [a.to_dict() for a in result]})

class RedisHandler(BaseHandler, ABC):
    @gen.coroutine
    def get(self):

        a = yield self.application.redis.ping()
        print(a)

class LoginHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def post(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            user = session.query(models.User).filter(models.User.username == req["username"]).one()
            if user.check_password(req["password"]):
                self.set_status(200)
            else:
                self.set_status(403)
            token = secrets.token_urlsafe()
            yield self.application.redis.set(user.username, token, ex=60*60*24)
            self.set_header("access-token", token)
            self.write({"results": "success"})

class AdminHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def post(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            access_token = self.request.headers.get("Access-Token")
            token = yield self.application.redis.get(req["username"])
            print(access_token)
            print(token)
            if token:
                if token.decode("utf-8") == access_token:

                    if req["type"] == "project":
                        results = {}
                        model = session.query(models.Project).order_by(desc(models.Project.date_created)).join(models.Author)
                        if req["term"] != "":
                            filter_list = [models.Project.title.ilike("%{}%".format(req["term"])), models.Author.name.ilike("%{}%".format(req["term"]))]
                            model = model.filter(or_(*filter_list))
                        page = Page(model, req["page"], req["per_page"])
                        results["results"] = page.values()
                        results["total_pages"] = page.total_pages()
                        results["count"] = page.count()
                        results["results"] = [r.to_dict() for r in results["results"]]
                        self.write(results)
            else:
                self.set_status(405, "Token invalid")

    @gen.coroutine
    def patch(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))
            access_token = self.request.headers.get("Access-Token")
            token = yield self.application.redis.get(req["username"])
            results = {}
            if token:
                if token.decode("utf-8") == access_token:
                    model = session.query(models.Project).filter(or_(*[models.Project.id == i for i in req["project_ids"]]))
                    for p in model.all():
                        results[p.id] = True
                        session.delete(p)
            session.flush()
            self.write(results)


class RawDataHandler(SessionMixin, BaseHandler, ABC):
    @gen.coroutine
    def post(self):
        with self.make_session() as session:
            req = json_decode(self.request.body.decode("utf-8"))


    @gen.coroutine
    def get(self, primary_id, project_id):
        with self.make_session() as session:
            project = session.query(models.Project).filter(models.Project.id == project_id).one()
            column_ids = []
            for f in project.files:
                if f.fileType == "Raw":
                    for c in f.sampleColumns:
                        column_ids.append(c.id)
            result = session.query(models.RawData)\
                .filter(or_(*[models.RawData.sampleColumn_id == c for c in column_ids]))\
                .filter(models.RawData.primary_id == primary_id).all()
            self.write({"results": [r.to_dict() for r in result]})


class SessionDataHandler(BaseHandler, ABC):
    @gen.coroutine
    def get(self, session_id):
        found = yield self.settings["motor_db"]["session"].find_one({"_id": session_id})
        found["_id"] = session_id
        self.write(found)

    @gen.coroutine
    def post(self):
        session = json_decode(self.request.body.decode("utf-8"))
        session["_id"] = str(ObjectId())
        new_session = yield self.settings["motor_db"]["session"].insert_one(session)
        self.write({"_id": new_session.inserted_id})

@dataclass
class Result:
    df: pd.DataFrame
    queryMap: dict

    def get_accession_from_query(self, primary_id):
        if primary_id in self.queryMap:
            return self.queryMap[primary_id]
        else:
            return None

@gen.coroutine
def get_uniprot(primary_ids: list[str], redis) -> Result:
    acc = set()
    queryMap = {}
    for a in primary_ids:
        for i in a.split(";"):
            accession = UniprotSequence(i.strip(), parse_acc=True)
            if accession.accession:
                acc.add(accession.accession)
                if a not in queryMap:
                    queryMap[i] = accession
    temp = [i for i in acc]
    temp_res = yield redis.get(";".join(temp))
    if temp_res:
        d = pd.read_csv(io.StringIO(temp_res.decode("utf-8")), sep="\t")
        d.rename(columns={d.columns[-1]: "query"}, inplace=True)
        return Result(df=d, queryMap=queryMap)
    parser = UniprotParser(acc, unique=True)
    df = []

    for res in parser.parse("tab", "post"):
        yield redis.set(";".join(temp), res, 60*60*24)
        d = pd.read_csv(io.StringIO(res), sep="\t")
        d.rename(columns={d.columns[-1]: "query"}, inplace=True)
        df.append(d)

    if len(df) > 1:
        return Result(df=pd.concat(df, ignore_index=True), queryMap=queryMap)
    else:
        return Result(df=df[0], queryMap=queryMap)
