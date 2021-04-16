from baguette import Baguette, View
from baguette.httpexceptions import BadRequest

app = Baguette(debug=True, error_response_type="json")

API_VERSION = "1.0"


@app.route("/", methods=["GET"])
async def index(request):
    return {"version": API_VERSION}


@app.route("/users")
class UserView(View):
    id = 1
    users = []  # TODO: use DB
    REQUIRED_FIELDS = {"name", "email"}
    # user: {"id": int, "name": str, "email": str}

    async def get(self, request):
        return self.users

    async def post(self, request):
        try:
            user = await request.json()
        except ValueError:
            raise BadRequest(description="Can't decode body as JSON")

        if type(user) is not dict:
            raise BadRequest(description="Dict required")

        if self.REQUIRED_FIELDS - set(user.keys()) != set():
            raise BadRequest(
                description="Must include: " + ", ".join(self.REQUIRED_FIELDS)
            )

        if set(user.keys()) - self.REQUIRED_FIELDS != set():
            raise BadRequest(
                description="Must only include: "
                + ", ".join(self.REQUIRED_FIELDS)
            )

        user["id"] = self.id
        self.users.append(user)
        self.id += 1

        return user
