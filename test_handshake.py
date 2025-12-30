import asyncio
import aiohttp
from uuid import uuid4
from datetime import datetime
import json


async def run_handshake_test():
    """
    Test the complete vertical slice handshake:
    1. Submit telemetry via FastAPI
    2. Worker processes it asynchronously
    3. Retrieve the calculated score
    """
    base_url = "http://localhost:8000"

    # Generate test data
    vehicle_id = str(uuid4())
    driver_id = str(uuid4())

    test_payload = {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": [
            {"speed_kmh": 50, "g_force_long": 0.1, "g_force_lat": 0.0},
            {
                "speed_kmh": 55,
                "g_force_long": -0.5,
                "g_force_lat": 0.0,
            },  # Harsh braking
            {"speed_kmh": 45, "g_force_long": 0.1, "g_force_lat": 0.0},
            {
                "speed_kmh": 50,
                "g_force_long": 0.6,
                "g_force_lat": 0.0,
            },  # Rapid acceleration
        ],
    }

    print("=" * 60)
    print("🚗 FleetFlow Vertical Slice Handshake Test")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        # Step 1: Submit telemetry
        print("\n1️⃣  Submitting telemetry...")
        async with session.post(
            f"{base_url}/api/v1/telemetry",
            json=test_payload,
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status == 202:
                result = await resp.json()
                trip_id = result["trip_id"]
                print(f"✅ Accepted: trip_id = {trip_id}")
            else:
                print(f"❌ Failed with status {resp.status}")
                return

        # Step 2: Wait for worker to process
        print("\n2️⃣  Waiting for worker to process (max 10s)...")
        await asyncio.sleep(2)

        # Step 3: Retrieve score
        print("\n3️⃣  Retrieving calculated score...")
        for attempt in range(10):
            await asyncio.sleep(1)
            async with session.get(f"{base_url}/api/v1/trip/{trip_id}/score") as resp:
                if resp.status == 200:
                    score = await resp.json()
                    print(f"✅ Score retrieved (attempt {attempt + 1}):")
                    print(f"   Safety Score: {score['safety_score']}/100")
                    print(f"   Harsh Braking Events: {score['harsh_braking_count']}")
                    print(f"   Rapid Acceleration Events: {score['rapid_accel_count']}")
                    print(f"   Created: {score['created_at']}")

                    print("\n" + "=" * 60)
                    print("✅ HANDSHAKE SUCCESSFUL!")
                    print("=" * 60)
                    return
                elif attempt < 9:
                    print(f"   ⏳ Still processing... (attempt {attempt + 1}/10)")

        print("\n❌ Score not available after 10 seconds")
        print("   Check worker logs: docker logs fleetflow-worker")


if __name__ == "__main__":
    asyncio.run(run_handshake_test())
