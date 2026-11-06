import httpx
import json

BASE_URL = "http://127.0.0.1:8700"

def main():
    print("=" * 50)
    print("FORMI - OUTCOME FIRST CONTROLLER")
    print("=" * 50)

    try:
        # Check simulator health
        response = httpx.get(f"{BASE_URL}/health", timeout=10)
        response.raise_for_status()

        print("\n1. SIMULATOR HEALTH")
        print(json.dumps(response.json(), indent=2))

        # Get simulator state
        response = httpx.get(f"{BASE_URL}/sim/state", timeout=10)
        response.raise_for_status()

        print("\n2. SIMULATOR STATE")
        print(json.dumps(response.json(), indent=2))

        # Get workflows
        response = httpx.get(f"{BASE_URL}/workflows", timeout=10)
        response.raise_for_status()

        workflows = response.json()

        print("\n3. AVAILABLE WORKFLOWS")
        print("Total workflows:", len(workflows))

        for workflow in workflows:
            wid = workflow["workflow_id"]

            print("\nWorkflow ID:", wid)

            config = httpx.get(
                f"{BASE_URL}/workflows/{wid}/config",
                timeout=10
            )
            config.raise_for_status()

            print("Configuration:")
            print(json.dumps(config.json(), indent=2))

        print("\nSUCCESS: CONTROLLER CONNECTED!")

    except httpx.ConnectError:
        print("ERROR: Simulator is not running.")
        print("Check your first terminal.")

    except Exception as error:
        print("ERROR:", error)


if __name__ == "__main__":
    main()
