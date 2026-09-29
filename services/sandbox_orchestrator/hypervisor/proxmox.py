from .base import HypervisorAdapter

class ProxmoxAdapter(HypervisorAdapter):
    def verify_isolation(self, vm_id: str) -> bool:
        raise NotImplementedError

    def get_vm_state(self, vm_id: str) -> str:
        raise NotImplementedError

    def start_vm(self, vm_id: str) -> bool:
        raise NotImplementedError

    def stop_vm(self, vm_id: str) -> bool:
        raise NotImplementedError

    def revert_to_snapshot(self, vm_id: str, snapshot_id: str) -> bool:
        raise NotImplementedError

    def execute_command_in_guest(self, vm_id: str, command: str) -> bool:
        raise NotImplementedError

    def transfer_file_to_guest(self, vm_id: str, source_path: str, dest_path: str) -> bool:
        raise NotImplementedError
