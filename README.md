# Real-time Acquisition of Photovoltaic Data  

This repository contains the implementation of a real-time data acquisition system for a photovoltaic (PV) installation. Using a **LabJack T7 Pro**, the system measures the current and voltage of the PV installation in real time. The acquired data is stored in both an SQLite database and a CSV file for traceability and analysis.  

---

## Features  

- **Real-Time Data Acquisition**: 
  - Current and voltage measurements are recorded every second using the LabJack T7 Pro.  
- **Automated Scheduling**: 
  - Data collection begins **5 minutes before sunrise** and pauses **5 minutes after sunset**, resuming automatically the next day.  
- **Data Storage**: 
  - Data is stored in two formats:
    - **SQLite Database** for structured querying and long-term storage.
    - **CSV Files** for easy access and analysis with tools like Excel or Python.  
- **Date-Based Organization**: 
  - Data is stored and organized by date for enhanced traceability.  

---

## Tools and Technologies  

- **Hardware**:  
  - **LabJack T7 Pro**: Used for precise voltage and current measurements.  

- **Programming Language**:  
  - **Python**: For interfacing with the LabJack T7 Pro and automating data collection.  

- **Libraries**:  
  - `labjack`: To communicate with the LabJack T7 Pro.  
  - `sqlite3`: For storing data in an SQLite database.  
  - `csv`: For creating and managing CSV files.  
  - `datetime`: For managing time-based operations such as sunrise/sunset tracking and date organization.  

---

## Project Structure  

