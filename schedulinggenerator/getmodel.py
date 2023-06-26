import requests as req
import os

work_dir_ = os.getcwd()
model_dir_ = work_dir_ + "/" + "gamodel"
model_file_path = model_dir_ + "/" + "gamodel.py"


class GetModel:
    def getModel(self, url=''):

        if not os.path.isdir(model_dir_):
            os.makedirs(model_dir_)

        if not os.path.isfile(model_file_path):
            req_model = req.get(url, allow_redirects=True)
            model_content = req_model.content

            with open(model_file_path, "wb") as file:
                file.write(model_content)
