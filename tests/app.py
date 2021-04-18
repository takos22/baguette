import baguette

app = baguette.Baguette(error_include_description=False)


@app.route("/")
async def index(request):
    return "Hello, world!"


@app.route("/json", methods=["GET", "POST"])
async def json(request):
    if request.method == "GET":
        return {"message": "Hello, World!"}
    elif request.method == "POST":
        return await request.json()
