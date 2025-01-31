import React, { useState } from "react";
import axios from "axios";
import { Button, Card, CardContent, Typography, CircularProgress } from "@mui/material";

function App() {
  const [invoice, setInvoice] = useState(null);
  const [packingSlip, setPackingSlip] = useState(null);
  const [shippingLabel, setShippingLabel] = useState(null);
  const [mergedPdf, setMergedPdf] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!invoice || !packingSlip || !shippingLabel) {
      alert("Please upload all three PDFs!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("invoice", invoice);
    formData.append("packing_slip", packingSlip);
    formData.append("shipping_label", shippingLabel);

    try {
      const response = await axios.post("https://shipmerge.onrender.com/upload", formData, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setMergedPdf(url);
    } catch (error) {
      console.error("Error merging PDFs", error);
      alert("Failed to merge PDFs. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div style={{ textAlign: "center", padding: "20px", maxWidth: "600px", margin: "auto" }}>
      <Typography variant="h4" gutterBottom>
        ShipMerge - Amazon PDF Merger
      </Typography>
      <Card variant="outlined" style={{ padding: "20px", marginBottom: "20px" }}>
        <CardContent>
          <Typography variant="h6">Upload Invoice</Typography>
          <input type="file" onChange={(e) => setInvoice(e.target.files[0])} />
        </CardContent>
      </Card>

      <Card variant="outlined" style={{ padding: "20px", marginBottom: "20px" }}>
        <CardContent>
          <Typography variant="h6">Upload Packing Slip</Typography>
          <input type="file" onChange={(e) => setPackingSlip(e.target.files[0])} />
        </CardContent>
      </Card>

      <Card variant="outlined" style={{ padding: "20px", marginBottom: "20px" }}>
        <CardContent>
          <Typography variant="h6">Upload Shipping Label</Typography>
          <input type="file" onChange={(e) => setShippingLabel(e.target.files[0])} />
        </CardContent>
      </Card>

      <Button 
        variant="contained" 
        color="primary" 
        onClick={handleUpload} 
        disabled={loading} 
        style={{ marginTop: "20px" }}
      >
        {loading ? <CircularProgress size={24} /> : "Merge PDFs"}
      </Button>

      {mergedPdf && (
        <div style={{ marginTop: "20px" }}>
          <Typography variant="h6">Download Merged PDF:</Typography>
          <a href={mergedPdf} download="merged_shipmerge.pdf">
            <Button variant="contained" color="secondary" style={{ marginTop: "10px" }}>
              Download PDF
            </Button>
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
