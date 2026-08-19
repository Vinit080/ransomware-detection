from abc import ABC, abstractmethod
from typing import Optional

class HypervisorAdapter(ABC):
    @abstractmethod
    def verify_isolation(self, vm_id: str) -> bool:
        """Verify the VM is isolated from production networks."""
        pass

    @abstractmethod
    def get_vm_state(self, vm_id: str) -> str:
        """Get the current power state of the VM."""
        pass

    @abstractmethod
    def start_vm(self, vm_id: str) -> bool:
        """Power on the VM."""
        pass

    @abstractmethod
    def stop_vm(self, vm_id: str) -> bool:
        """Power off the VM."""
        pass

    @abstractmethod
    def revert_to_snapshot(self, vm_id: str, snapshot_id: str) -> bool:
        """Revert the VM to a known clean snapshot."""
        pass

    @abstractmethod
    def execute_command_in_guest(self, vm_id: str, command: str) -> bool:
        """Execute a command inside the guest OS."""
        pass

    @abstractmethod
    def transfer_file_to_guest(self, vm_id: str, source_path: str, dest_path: str) -> bool:
        """Transfer a file into the guest OS."""
        pass
