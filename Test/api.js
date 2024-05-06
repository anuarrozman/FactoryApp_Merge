const express = require('express');
const app = express();

// Mock device data
const devices = [
    { serial_no: "A00000005", mac_address: "xxxx" , matter_cert_id: "9d442a79-1f15-429e-815f-77caa3050562"},
    { serial_no: "A00000006", mac_address: "yyyy" , matter_cert_id: "ed39c959-d7c9-459b-88d8-2675b7cc4e41"},
    { serial_no: "A00000007", mac_address: "zzzz" , matter_cert_id: "8aba3236-04c9-4dba-a1fe-d8d90025f406"},
    { serial_no: "A00000008", mac_address: "aaaa" , matter_cert_id: "304fadbb-21bd-451d-9425-42564555f6d0"},
    { serial_no: "A00000009", mac_address: "bbbb" , matter_cert_id: "0e826ae7-2f8a-47d1-bc33-82f90e9cf7a6"}
];

// Endpoint to retrieve device data
app.get('/devices', (req, res) => {
    res.json(devices);
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

