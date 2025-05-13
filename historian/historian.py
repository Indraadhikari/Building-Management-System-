import graphene
from influxdb_client import InfluxDBClient

class SensorData(graphene.ObjectType):
    temperature = graphene.Float()
    humidity = graphene.Float()
    energy_usage = graphene.Float()

class Query(graphene.ObjectType):
    sensor_data = graphene.List(SensorData)

    def resolve_sensor_data(self, info):
        client = InfluxDBClient(url="http://localhost:8086", token="my-token", org="my-org")
        query_api = client.query_api()
        result = query_api.query('''
            from(bucket: "sensor_bucket")
            |> range(start: -1h)
        ''')
        return [SensorData(**point) for point in result.records]

schema = graphene.Schema(query=Query)