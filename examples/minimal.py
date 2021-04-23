from baguette import Baguette, View

app = Baguette(error_response_type="html")


@app.route("/")
async def index(request):
    return '<h1>Hello world</h1>\n<a href="/home">Home</a>'


@app.route("/home")
class Home(View):
    home_text = "<h1>Home</h1>"

    async def get(self):
        return self.home_text

    async def post(self, request):
        self.home_text = await request.body()
        return self.home_text
