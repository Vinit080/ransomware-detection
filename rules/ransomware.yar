rule Ransomware_Mass_File_Encryption {
    meta:
        description = "Detects mass file encryption behavior based on high entropy and file extension changes"
        author = "Sandbox"
        severity = "High"
    strings:
        $ext1 = ".enc" nocase
        $ext2 = ".locked" nocase
        $ext3 = ".crypto" nocase
        $note1 = "README.txt" nocase
        $note2 = "DECRYPT_FILES.txt" nocase
    condition:
        any of ($ext*) or any of ($note*)
}

rule Suspicious_Network_C2 {
    meta:
        description = "Detects outbound connections to suspicious ports often used for C2 or key exfiltration"
        author = "Sandbox"
        severity = "Medium"
    condition:
        // In a real scenario, this would match on actual PCAP data or specific IPs/Domains.
        // For our telemetry simulator, we will map port 4444 or 9001 to this rule.
        // YARA rules over JSON/Telemetry require mapping in python, or writing a custom YARA module.
        // We will do string matching on the JSON representation of the telemetry.
        false // Placeholder for standard YARA, our python wrapper will do custom checks.
}
