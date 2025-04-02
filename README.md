# 4llDos
Advanced DoS Testing Tool ⚠ Legal Disclaimer: This tool is for authorized penetration testing and security research only. Unauthorized use is illegal. Always obtain explicit written permission before testing any system.  

# Installation & Usage

1)kali@kali-$ 
    git clone https://github.com/RadinRodrigo/4llDos.git

2)kali@kali-$
    cd advanced-dos-tester

3)kali@kali-$ 
    python3 advanced_dos_tester.py <TARGET_IP> -p <PORT> -t <TPS> -m <METHOD> -d <DURATION>

Example (Authorized Testing):

# TCP SYN Flood (100 TPS for 30 seconds)
kali@kali-$ 
    python3 advanced_dos_tester.py 192.168.1.100 -p 80 -t 100 -m tcp -d 30
