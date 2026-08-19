import time
from .base import HypervisorAdapter

class MockHypervisorAdapter(HypervisorAdapter):
    def __init__(self):
        self.state = "STOPPED"
        self.isolated = True

    def verify_isolation(self, vm_id: str) -> bool:
        time.sleep(0.5)
        return self.isolated

    def get_vm_state(self, vm_id: str) -> str:
        return self.state

    def start_vm(self, vm_id: str) -> bool:
        time.sleep(1)
        self.state = "RUNNING"
        return True

    def stop_vm(self, vm_id: str) -> bool:
        time.sleep(1)
        self.state = "STOPPED"
        return True

    def revert_to_snapshot(self, vm_id: str, snapshot_id: str) -> bool:
        time.sleep(2)
        self.state = "STOPPED"
        return True

    def execute_command_in_guest(self, vm_id: str, command: str) -> bool:
        time.sleep(0.5)
        return True

    def transfer_file_to_guest(self, vm_id: str, source_path: str, dest_path: str) -> bool:
        time.sleep(0.5)
        return True
