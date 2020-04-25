import asyncio
from bleak import BleakClient

address = "00:16:53:B7:14:55"
MODEL_NBR_UUID = "7231E8ED-7F46-45E4-BC4E-8001D1C55EC1"


async def run(address, loop):
    async with BleakClient(address, loop=loop) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))
