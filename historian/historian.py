import os
import asyncio
from aiohttp import web
from graphene import ObjectType, String, Float, List, Field, Schema
from influxdb_client import InfluxDBClient

INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("ORG")
BUCKET = os.getenv("BUCKET")

# Initialize InfluxDB client
influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
query_api = influx.query_api()

class DataPoint(ObjectType):
    time = String()
    sensor_id = String()
    temperature = Float()
    humidity = Float()
    energy_kwh = Float()

class AggregatedDataPoint(ObjectType):
    time = String()
    sensor_id = String()
    avg_temperature = Float()

class Query(ObjectType):
    raw_data = List(DataPoint, sensor_id=String(required=True))
    aggregated_data = List(AggregatedDataPoint, sensor_id=String(required=True))

    def resolve_raw_data(root, info, sensor_id):
        query = f'''
            from(bucket: "{BUCKET}")
              |> range(start: -1h)
              |> filter(fn: (r) => r._measurement == "raw_data" and r.sensor_id == "{sensor_id}")
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
              |> keep(columns: ["_time", "sensor_id", "temperature", "humidity", "energy_kwh"])
        '''
        result = query_api.query_data_frame(query)
        return [
            DataPoint(
                time=row["_time"].isoformat(),
                sensor_id=row["sensor_id"],
                temperature=row["temperature"],
                humidity=row["humidity"],
                energy_kwh=row["energy_kwh"]
            )
            for _, row in result.iterrows()
        ]

    def resolve_aggregated_data(root, info, sensor_id):
        query = f'''
            from(bucket: "{BUCKET}")
              |> range(start: -1h)
              |> filter(fn: (r) => r._measurement == "aggregated_data" and r.sensor_id == "{sensor_id}")
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
              |> keep(columns: ["_time", "sensor_id", "avg_temperature"])
        '''
        result = query_api.query_data_frame(query)
        return [
            AggregatedDataPoint(
                time=row["_time"].isoformat(),
                sensor_id=row["sensor_id"],
                avg_temperature=row["avg_temperature"]
            )
            for _, row in result.iterrows()
        ]

schema = Schema(query=Query)

# GraphQL HTTP handler
async def handle_graphql(request):
    data = await request.json()
    result = schema.execute(data.get('query'))
    return web.json_response(result.to_dict())

app = web.Application()
app.router.add_post("/graphql", handle_graphql)

if __name__ == "__main__":
    web.run_app(app, port=8088)
