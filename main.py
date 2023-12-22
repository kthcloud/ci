import os
import time
import sys
from dotenv import load_dotenv

load_dotenv()
import datetime
import iam
import vms


def setup():
    print(
        """        ____       __   __  __         __                __
     __/  __\\     / /__/ /_/ /_  _____/ /___  __  ______/ /
   _/  __/   \\   / //_/ __/ __ \\/ ___/ / __ \\/ / / / __  /
  /          |  / ,< / /_/ / / / /__/ / /_/ / /_/ / /_/ /
  \\__________/ /_/|_|\\__/_/ /_/\\___/_/\\____/\\__,_/\\__,_/   """
    )

    print("🏃 Starting test suite")


def cleanup():
    print(f"⌛ Done in {str(time.time() - timer).split('.')[0]} seconds")
    print(f"✅ Passed {len(passed)} tests")

    if len(failed) > 0:
        print(f"❌ Failed {len(failed)} tests")

        for fail in failed:
            print(f"\t➡️  {fail}")

        print("😔 Better luck next time!")
    else:
        print("🎉 Great job!")

    # write a report to a file
    with open("report.txt", "w") as f:
        f.write(f"kthcloud ci - report of {datetime.datetime.now()}\n")
        f.write(f"✅ Passed {len(passed)} tests\n")
        f.write(f"❌ Failed {len(failed)} tests\n")
        for fail in failed:
            f.write(f"\t➡️  {fail}\n")
        f.write(f"⌛ Done in {str(time.time() - timer).split('.')[0]} seconds\n")

        if len(failed) > 0:
            f.write("😔 Better luck next time!\n")
        else:
            f.write(f"👍 Great job!\n")


def get_accounts():
    accounts_raw = os.getenv("kthcloud_test_accounts")
    if not accounts_raw:
        raise ValueError("Environment variable kthcloud_test_accounts not set")

    accounts_arr = accounts_raw.split(",")
    accounts = []
    for account in accounts_arr:
        acc = account.split(":")
        accounts.append({"username": acc[0], "password": acc[1]})

    print(
        f"{len(accounts)} accounts to test: {', '.join(map(lambda x: x['username'], accounts))}"
    )

    for i, account in enumerate(accounts):
        progress = ["⌛", "⏳"]
        sys.stdout.write(
            f"\r{progress[i%2]} Checking {i+1} of {len(accounts)} accounts"
        )
        sys.stdout.flush()
        try:
            token = iam.get_oidc_token(account["username"], account["password"])
            if not token:
                raise Exception("Failed to get token")

        except Exception as e:
            failed.append(f"Failed to get token for {account['username']}")
            continue

        passed.append(f"✔️ Got token for {account['username']}")
        account["token"] = token

    print("\n")
    return accounts


def create_vms():
    pubkey = os.getenv("ssh_pubkey")

    vm_ids = []
    i = 0
    for j, account in enumerate(accounts):
        num = 0
        while True:
            i += 1
            progress = ["🔨", "⚒️ "]
            sys.stdout.write(
                f"\r{progress[i%2]} {len(vm_ids)} vms created, account {j+1} of {len(accounts)}"
            )
            sys.stdout.flush()
            num += 1
            try:
                vm = vms.create_vm(
                    account["token"],
                    {
                        "name": f"test-vm-{account['username'].split('@')[0]}-{num}",
                        "sshPublicKey": pubkey,
                        "cpuCores": 2,
                        "diskSize": 20,
                        "ram": 4,
                        "zone": zone,
                    },
                )
                if not vm:
                    raise Exception("Failed to create vm")
            except Exception:
                if num == 1:
                    failed.append(f"Failed to create vm for {account['username']}")
                break

            passed.append(f"✔️ Created vm for {account['username']}")
            if "vms" in account.keys():
                account["vms"].append(vm)
            else:
                account["vms"] = [vm]
            vm_ids.append(vm)
            time.sleep(5)

    print("\n")
    print(f"🥹  Created {len(vm_ids)} vms")
    return vm_ids


def await_vm_ready():
    print(f"👀 Checking {len(vm_ids)} vms")
    start_time = time.time()
    done = set()
    errored = set()

    i = 0
    while True:
        i += 1
        for account in accounts:
            if "vms" not in account.keys():
                continue
            for vm_id in account["vms"]:
                if vm_id in done or vm_id in errored:
                    continue
                try:
                    vm = vms.get_vm(account["token"], vm_id)
                    if not vm:
                        raise Exception("Server did not return a valid JSON response")

                    if vm["status"] == "resourceNotFound":
                        raise Exception("resourceNotFound")

                except Exception as e:
                    failed.append(
                        f"Failed to get vm {vm_id} for {account['username']}, reason: {e}"
                    )
                    errored.add(vm_id)
                    break

                if vm["status"] == "resourceRunning":
                    done.add(vm_id)

        if len(done) == len(vm_ids):
            return

        if len(errored) == len(vm_ids):
            failed.append(f"Failed to get any vms")
            break

        progress = ["⌛", "⏳"]
        sys.stdout.write(
            f"\r{progress[i%2]} {len(done)} of {len(vm_ids)} vms ready, {len(errored)} errored"
        )
        sys.stdout.flush()

        time.sleep(1)

        if time.time() - start_time > 300:
            failed.append(f"Reason: VM creation timed out")
            break

    print("\n")
    return


def delete_vms():
    print(f"🗑️  Deleting all vms")
    i = 0
    for account in accounts:
        cleanup = vms.get_vms(account["token"])

        for vm in cleanup:
            i += 1
            try:
                vms.delete_vm(account["token"], vm["id"])
                progress = ["⌛", "⏳"]
                sys.stdout.write(f"\r{progress[i%2]} Deleting vms...")
                sys.stdout.flush()
            except Exception as e:
                failed.append(f"Failed to delete vm for {account['username']}")
                break

            passed.append(f"✔️ Deleted vm for {account['username']}")

    print("\n")
    return


if __name__ == "__main__":
    # Preparations
    setup()
    failed = []
    passed = []
    timer = time.time()

    zones = os.getenv("kthcloud_zones")

    if not zones:
        raise ValueError("Environment variable kthcloud_zones not set")

    zones = zones.split(",")

    for zone in zones:
        print(f"🔎 Checking zone {zone}")

        # Tests
        accounts = get_accounts()
        vm_ids = create_vms()
        await_vm_ready()

        #
        # do some stuff
        #

        delete_vms()

    cleanup()
