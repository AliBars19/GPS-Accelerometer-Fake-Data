# 🛰️ Formula Student CAN → JSON → MCAP Converter (GPS Data)

This repository documents our process for converting **raw CAN data** from the **GPS Node** on the vehicle into an **MCAP file** for downstream processing, storage, or visualization.

---

## 📖 Overview

Our vehicle’s GPS sensors send telemetry data over the **CAN bus** — encoded as 8-byte binary messages.  
To make this data readable and compatible with analysis tools, we convert each CAN frame into a structured **JSON object** 

---

## Features



- Download CAN bus data from a public JSON file  
- Store messages in an MCAP file with a defined schema  
- Read back and print the first few messages  

---

## ⚙️ Requirements

-python 3.11+
-packages
    - 'mcap'
    -'requests'
