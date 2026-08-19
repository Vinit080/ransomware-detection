import subprocess
import logging
from typing import Optional
from .base import HypervisorAdapter

logger = logging.getLogger(__name__)

class VirtualBoxAdapter(HypervisorAdapter):
    def _run_vboxmanage(self, *args) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(["vboxmanage"] + list(args), capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"vboxmanage command failed: {' '.join(args)}\nError: {e.stderr}")
            raise

    def verify_isolation(self, vm_id: str) -> bool:
        # Check if the VM's network adapters are set to Internal or Host-Only
        try:
            result = self._run_vboxmanage("showvminfo", vm_id, "--machinereadable")
            # Basic check: Ensure no NAT or Bridged interfaces are active
            if 'nic1="nat"' in result.stdout or 'nic1="bridged"' in result.stdout:
                logger.warning(f"VM {vm_id} is not isolated (NAT/Bridged detected).")
                return False
            return True
        except Exception:
            return False

    def get_vm_state(self, vm_id: str) -> str:
        try:
            result = self._run_vboxmanage("showvminfo", vm_id, "--machinereadable")
            for line in result.stdout.splitlines():
                if line.startswith("VMState="):
                    state = line.split("=")[1].strip('"')
                    return state.upper()
            return "UNKNOWN"
        except Exception:
            return "ERROR"

    def start_vm(self, vm_id: str) -> bool:
        try:
            self._run_vboxmanage("startvm", vm_id, "--type", "headless")
            return True
        except Exception:
            return False

    def stop_vm(self, vm_id: str) -> bool:
        try:
            self._run_vboxmanage("controlvm", vm_id, "poweroff")
            return True
        except Exception:
            return False

    def revert_to_snapshot(self, vm_id: str, snapshot_id: str) -> bool:
        try:
            # Must be powered off to restore snapshot safely
            state = self.get_vm_state(vm_id)
            if state in ["RUNNING", "PAUSED"]:
                self.stop_vm(vm_id)
            self._run_vboxmanage("snapshot", vm_id, "restore", snapshot_id)
            return True
        except Exception:
            return False

    def execute_command_in_guest(self, vm_id: str, command: str) -> bool:
        try:
            # For a real sandbox, credentials would be injected via env vars or secure vault
            self._run_vboxmanage("guestcontrol", vm_id, "run", "--exe", command, "--username", "Admin", "--password", "admin", "--wait-stdout")
            return True
        except Exception:
            return False

    def transfer_file_to_guest(self, vm_id: str, source_path: str, dest_path: str) -> bool:
        try:
            self._run_vboxmanage("guestcontrol", vm_id, "copyto", "--target-directory", dest_path, source_path, "--username", "Admin", "--password", "admin")
            return True
        except Exception:
            return False
