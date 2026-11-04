<h1>Intelligent Shopping Cart with Embedded Scanner and Weight Sensor Technology for Anti-Theft and Inventory Tracking</h1>

Developed an Intelligent Shopping Cart leveraging Raspberry Pi, Camera, RFID, Load Cells, 
and ESP32 for real-time billing, product identification, weight validation, and theft 
prevention. Integrated with a MongoDB-based billing system for automated balance 
deduction and cloud-synced inventory management.
<img width="1062" height="870" alt="smart_cart" src="https://github.com/user-attachments/assets/1209993a-ee35-4a39-bf95-524576689d8d" />


<img width="875" height="429" alt="image" src="https://github.com/user-attachments/assets/2d3c59a8-e106-485b-a588-644b74a3860d" />

<h2>System Interface</h2>
The smart shopping cart integrates six interconnected subsystems managed by a 
Raspberry Pi 3/4, which serves as the central processing unit. Each subsystem is 
carefully designed to ensure real-time operation, system safety, and a seamless shopping 
experience. Below is the technical breakdown of each subsystem: 
<img width="918" height="467" alt="image" src="https://github.com/user-attachments/assets/3b93041a-d017-4ae0-bb43-a5a784278671" />

<h3>Billing System</h3>
The billing system integrates an MFRC522 RFID Reader (Figure 6.1) and RFID 
Cards. The RFID Reader operates at 13.56MHz and supports communication protocols 
like SPI, I2C, and UART, offering fast and reliable tag detection with a read range of 
approximately 5cm. It features low power consumption (13-26mA) and supports 
multiple data rates up to 10Mbps.  

<img width="640" height="383" alt="image" src="https://github.com/user-attachments/assets/1fa02e69-0564-4eec-9b6c-754ef91b0807" />


<h3>Weight Sensing System</h3>
The Avery LM10 weighing indicator supports multiple internal configuration 
groups. After experimenting with all combinations of parameters setting, Two distinct sets of parameter configurations were evaluated: 
• Set A (High Fluctuation): Included minimal filtering and fast zero-tracking, 
which resulted in frequent fluctuations even with constant load. 
• Set B (Optimized – Final Settings): Final optimized settings after calibration 
with known weights resulted in stable readings with minimal drift, ensuring 
reliable performance during billing and theft detection processes. 
<img width="776" height="340" alt="image" src="https://github.com/user-attachments/assets/2662856d-5b7a-467e-a9dc-4cc94fe19534" />

These parameters were finalized after calibration with known standard weights, ensuring measurement reliability in the 
operational environment. The system was calibrated to detect weights as low as 5 grams, validating its sensitivity 
for small items like spices or confectionery.

<h3>Power Consumption</h3>
After careful testing, we came to conclusion that:
1. A single 18650 Battery Shield V3 configuration maintained stable 5V output but 
still exhibited voltage drops under load 
2. A three-cell 18650 setup with XL4015 buck converter failed to reliably power 
peripherals, with only the Raspberry Pi showing intermittent operation.

Thus, for the current prototype deployment, we proceeded with the power 
bank solution while documenting its limitations.

<h3>Camera Selection</h3>
Multiple camera modules were evaluated during the development phase for 
barcode scanning, including the Raspberry Pi Camera Module V2, the Raspberry Pi HQ 
Camera, Arducam, and third-party USB webcams. A comparative analysis was 
conducted based on factors such as autofocus capability, image clarity, edge sharpness 
(critical for barcode recognition), distortion levels, and overall cost-effectiveness.
Visual results of comparison of different cameras are given below:
<img width="689" height="363" alt="image" src="https://github.com/user-attachments/assets/f6a1e005-c5b2-478c-b219-06b101d2b5e2" />
<img width="716" height="392" alt="image" src="https://github.com/user-attachments/assets/d45f8398-4500-4113-ad01-7e60fbf70f06" />
<img width="717" height="436" alt="image" src="https://github.com/user-attachments/assets/6efcaecf-c84c-48f2-b147-1dcc9cb54bad" />
Overall, the Camera Module 3 
provided the best compromise between technical performance and cost efficiency for 
the dynamic retail environment targeted by the smart shopping cart system. 

<h3>Hardware Integration</h3>
After individual testing and verification of all system modules—namely the 
billing unit, barcode scanner, RFID reader, weight sensor system, power management, 
and the graphical user interface—the final phase involved integrating all hardware 
components into a single, compact enclosure. A custom-designed acrylic or ABS plastic case was fabricated to house the Raspberry Pi 4, power circuitry, and peripheral connections. Care was taken to ensure sufficient ventilation and accessibility to ports for debugging or maintenance. Cable management was optimized to avoid clutter and accidental disconnections, especially given the mobile nature of the cart. 
<img width="532" height="173" alt="image" src="https://github.com/user-attachments/assets/ac591a09-7027-4dd6-aa62-bd3dbc5b2d4b" />

<h3>Software Integration</h3>
The user interface was developed using Python’s Tkinter library and tested on a 
7-inch capacitive touchscreen display. During operation, the GUI dynamically updated 
in real time to display scanned items, individual prices, cumulative weight, and the total 
bill amount. Visual feedback mechanisms, such as red-colored alerts for weight 
mismatches or invalid barcode scans, were incorporated to enhance user awareness and 
system reliability. 
The interface maintained responsive performance even during rapid scanning 
sequences. The layout was designed to be user-friendly and intuitive, with clearly 
labeled buttons for actions such as item removal, help requests, and purchase 
confirmation. Throughout testing, the GUI operated seamlessly on the Raspberry Pi and 
maintained stable communication with the MongoDB database, with no significant 
latency or performance bottlenecks observed. 
<img width="1845" height="538" alt="image" src="https://github.com/user-attachments/assets/9d19fcc1-6733-4564-8797-591838bcc23d" />

<img width="768" height="355" alt="image" src="https://github.com/user-attachments/assets/a5daf5c2-1ab0-4655-bd58-807b9887bd1b" />

