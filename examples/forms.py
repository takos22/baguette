from baguette import Baguette, View
from baguette.httpexceptions import BadRequest

app = Baguette(error_response_type="html")


FORM_HTML = """
<form action="/" method="POST">
  <div>
    <label for="say">What greeting do you want to say?</label>
    <input name="say" id="say" value="Hi">
  </div>
  <div>
    <label for="to">Who do you want to say it to?</label>
    <input name="to" id="to" value="Mom">
  </div>
  <div>
    <button>Send my greetings</button>
  </div>
</form>
"""

FILE_FORM_HTML = """
<form action="/file" method="POST" enctype="multipart/form-data">
  <div>
    <label for="file">Choose a file</label>
    <input name="file" type="file" id="file">
  </div>
  <div>
    <button>Send the file</button>
  </div>
</form>
"""


@app.route("/")
class Form(View):
    async def get(self):
        return FORM_HTML

    async def post(self, request):
        form = await request.form()
        return '<h1>Said "{}" to {}</h1>'.format(form["say"], form["to"])


@app.route("/file")
class FileForm(View):
    async def get(self):
        return FILE_FORM_HTML

    async def post(self, request):
        form = await request.form()
        if not form["file"].is_file:
            raise BadRequest("Form value 'file' isn't a file")
        return "<h1>Uploaded {}</h1>\nIt's content is:<pre>{}</pre>".format(
            form["file"].filename, form["file"].text
        )


if __name__ == "__main__":
    app.run()
