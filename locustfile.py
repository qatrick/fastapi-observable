from locust import HttpUser, task, between

class FastAPILoadTest(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def browse_home(self):
        self.client.get("/", name="Home Page")

    @task(1)
    def heavy_task(self):
        self.client.get("/heavy", name="Heavy Computation")