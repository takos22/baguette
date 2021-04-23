from baguette import Baguette, View
from baguette.httpexceptions import BadRequest, NotFound
from baguette.responses import EmptyResponse

app = Baguette(debug=True, error_response_type="json")

API_VERSION = "1.0"
REQUIRED_FIELDS = {"name", "email"}

users = {}  # TODO: use DB
# user: {"id": int, "name": str, "email": str}


@app.route("/", methods=["GET"])
async def index():
    return {"version": API_VERSION}


@app.route("/users")
class UserList(View):
    id = 1

    async def get(self):
        return list(users.values())

    async def post(self, request):
        try:
            user = await request.json()
        except ValueError:
            raise BadRequest(description="Can't decode body as JSON")

        if not isinstance(user, dict):
            raise BadRequest(description="Dict required")

        if REQUIRED_FIELDS - set(user.keys()) != set():
            raise BadRequest(
                description="Must include: " + ", ".join(self.REQUIRED_FIELDS)
            )

        if set(user.keys()) - REQUIRED_FIELDS != set():
            raise BadRequest(
                description="Must only include: " + ", ".join(REQUIRED_FIELDS)
            )

        user["id"] = self.id
        users[user["id"]] = user
        self.id += 1

        return user


@app.route("/users/<user_id:int>")
class UserDetail(View):
    async def get(self, user_id: int):
        if user_id not in users:
            raise NotFound(description=f"No user with ID {user_id}")

        return users[user_id]

    async def delete(self, user_id: int):
        if user_id not in users:
            raise NotFound(description=f"No user with ID {user_id}")

        del users[user_id]
        return EmptyResponse()
