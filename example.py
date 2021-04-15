from baguette import Baguette, View

app = Baguette()


@app.route("/")
@app.route("/index")
async def index(request):
    return "<h1>Hello world</h1>"


@app.route("/home")
class Home(View):
    home_text = "<h1>Home</h1>"

    async def get(self, request):
        return self.home_text

    async def post(self, request):
        self.home_text = await request.body()
        return self.home_text
